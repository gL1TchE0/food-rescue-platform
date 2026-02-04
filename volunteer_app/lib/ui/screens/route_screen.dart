import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform, TargetPlatform;
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter_polyline_points/flutter_polyline_points.dart';
import '../../data/task_model.dart';
import '../../data/location_service.dart';
import '../widgets/qr_scanner_modal.dart';
import '../../data/task_api_service.dart';

/// Route Screen - Navigation & QR Verification
/// Shows Google Maps with route from volunteer location to destination
/// Handles QR code scanning for pickup/delivery verification
class RouteScreen extends StatefulWidget {
  final Task task;

  const RouteScreen({super.key, required this.task});

  @override
  State<RouteScreen> createState() => _RouteScreenState();
}

class _RouteScreenState extends State<RouteScreen> {
  GoogleMapController? _mapController;
  Position? _currentPosition;
  final LocationService _locationService = LocationService.instance;
  final TaskApiService _taskApi = TaskApiService();
  
  Set<Marker> _markers = {};
  Set<Polyline> _polylines = {};
  PolylinePoints polylinePoints = PolylinePoints();
  
  bool _isLoading = true;
  String? _errorMessage;
  
  // Keep a mutable copy of the task for status updates
  late Task _currentTask;
  
  // Real-time tracking
  StreamSubscription<Position>? _locationSubscription;
  double? _distanceToDestination;
  double? _currentSpeed; // in m/s
  String? _estimatedTimeArrival;
  
  // Check if platform supports Google Maps
  bool get _isMapSupported => 
      defaultTargetPlatform == TargetPlatform.android ||
      defaultTargetPlatform == TargetPlatform.iOS;

  @override
  void initState() {
    super.initState();
    _currentTask = widget.task;
    _initializeMap();
    _startLocationTracking();
  }

  @override
  void dispose() {
    _locationSubscription?.cancel();
    _mapController?.dispose();
    super.dispose();
  }

  Future<void> _initializeMap() async {
    try {
      // Get current location
      final position = await _locationService.getCurrentLocation();
      setState(() {
        _currentPosition = position;
      });

      // Set up markers and route
      await _setupMarkersAndRoute();
      
      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Error initializing map: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _setupMarkersAndRoute() async {
    if (_currentPosition == null) return;

    // Determine destination based on task status
    final destination = _getDestination();
    
    // Add markers
    _markers = {
      // Current location marker
      Marker(
        markerId: const MarkerId('current_location'),
        position: LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
        infoWindow: const InfoWindow(title: 'Your Location'),
      ),
      // Destination marker
      Marker(
        markerId: MarkerId(destination.type),
        position: LatLng(destination.lat, destination.lng),
        icon: BitmapDescriptor.defaultMarkerWithHue(
          destination.type == 'pickup' 
              ? BitmapDescriptor.hueGreen 
              : BitmapDescriptor.hueRed,
        ),
        infoWindow: InfoWindow(
          title: destination.type == 'pickup' ? 'Pickup Location' : 'Delivery Location',
        ),
      ),
    };

    // Draw route
    await _drawRoute(
      LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
      LatLng(destination.lat, destination.lng),
    );
  }

  ({String type, double lat, double lng}) _getDestination() {
    // If task is ASSIGNED or NAVIGATING_TO_DONOR, destination is pickup location
    if (widget.task.status == TaskStatus.assigned ||
        widget.task.status == TaskStatus.inProgress) {
      return (
        type: 'pickup',
        lat: widget.task.pickupLocation.lat,
        lng: widget.task.pickupLocation.lng,
      );
    }
    
    // If task is PICKED_UP or IN_TRANSIT, destination is drop location
    return (
      type: 'delivery',
      lat: widget.task.dropLocation.lat,
      lng: widget.task.dropLocation.lng,
    );
  }

  Future<void> _drawRoute(LatLng start, LatLng end) async {
    // Note: For production, you'll need a Google Maps API key
    // and use the Directions API. This is a simplified version
    // that draws a straight line. Replace with actual API call.
    
    List<LatLng> polylineCoordinates = [];
    
    try {
      // TODO: Replace with actual Google Directions API call
      // For now, drawing a simple straight line
      polylineCoordinates = [start, end];
      
      setState(() {
        _polylines.add(
          Polyline(
            polylineId: const PolylineId('route'),
            color: Colors.blue,
            width: 5,
            points: polylineCoordinates,
          ),
        );
      });
    } catch (e) {
      print('Error drawing route: $e');
    }
  }

  void _startLocationTracking() {
    print('Starting live location tracking...');
    _locationSubscription = _locationService.startLocationStream().listen(
      (Position position) {
        _updateLocation(position);
      },
      onError: (error) {
        print('Location tracking error: $error');
      },
    );
  }

  void _updateLocation(Position position) {
    if (!mounted) return;

    setState(() {
      _currentPosition = position;
      _currentSpeed = position.speed; // in m/s
    });

    // Calculate distance to destination
    final destination = _getDestination();
    final distanceInMeters = _locationService.calculateDistance(
      position.latitude,
      position.longitude,
      destination.lat,
      destination.lng,
    );

    setState(() {
      _distanceToDestination = distanceInMeters / 1000; // Convert to km
      
      // Calculate ETA (simple estimation)
      if (_currentSpeed != null && _currentSpeed! > 0.5) {
        // Only calculate if moving faster than 0.5 m/s (1.8 km/h)
        final timeInSeconds = distanceInMeters / _currentSpeed!;
        final minutes = (timeInSeconds / 60).round();
        _estimatedTimeArrival = minutes > 60 
            ? '${(minutes / 60).floor()}h ${minutes % 60}m'
            : '${minutes}m';
      } else {
        _estimatedTimeArrival = '--';
      }
    });

    // Update the blue marker position
    _updateCurrentLocationMarker();

    // Animate camera to follow user
    _mapController?.animateCamera(
      CameraUpdate.newLatLng(
        LatLng(position.latitude, position.longitude),
      ),
    );

    print('Position updated: ${position.latitude}, ${position.longitude} | Speed: ${position.speed} m/s | Distance: ${_distanceToDestination?.toStringAsFixed(2)} km');
  }

  void _updateCurrentLocationMarker() {
    if (_currentPosition == null) return;

    final destination = _getDestination();
    
    setState(() {
      _markers = {
        // Current location marker (blue)
        Marker(
          markerId: const MarkerId('current_location'),
          position: LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
          infoWindow: InfoWindow(
            title: 'You',
            snippet: 'Speed: ${(_currentSpeed ?? 0).toStringAsFixed(1)} m/s',
          ),
          rotation: _currentPosition!.heading,
        ),
        // Destination marker
        Marker(
          markerId: MarkerId(destination.type),
          position: LatLng(destination.lat, destination.lng),
          icon: BitmapDescriptor.defaultMarkerWithHue(
            destination.type == 'pickup' 
                ? BitmapDescriptor.hueGreen 
                : BitmapDescriptor.hueRed,
          ),
          infoWindow: InfoWindow(
            title: destination.type == 'pickup' ? 'Pickup Location' : 'Delivery Location',
            snippet: '${_distanceToDestination?.toStringAsFixed(2) ?? "N/A"} km away',
          ),
        ),
      };
    });
  }


  void _openQRScanner() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => QRScannerModal(
        onScanComplete: _handleQRScan,
      ),
    );
  }

  Future<void> _handleQRScan(String qrCode) async {
    // Close the scanner modal
    if (mounted) Navigator.pop(context);

    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    try {
      bool success = false;
      String message = '';

      // Determine which verification to perform based on task status
      if (_currentTask.status == TaskStatus.assigned ||
          _currentTask.status == TaskStatus.inProgress) {
        // Verify pickup
        success = await _taskApi.verifyPickup(_currentTask.id, qrCode);
        message = success 
            ? 'Pickup verified! Proceeding to delivery location.'
            : 'Invalid pickup QR code.';
      } else if (_currentTask.status == TaskStatus.pickedUp ||
          _currentTask.status == TaskStatus.inTransit) {
        // Verify delivery
        success = await _taskApi.verifyDelivery(_currentTask.id, qrCode);
        message = success
            ? 'Delivery verified! Task completed.'
            : 'Invalid delivery QR code.';
      }

      // Close loading dialog
      if (mounted) Navigator.pop(context);

      // Show result
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: success ? Colors.green : Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );

        // If successful, update the UI or navigate back
        if (success) {
          // Check if this was pickup or delivery
          if (_currentTask.status == TaskStatus.assigned ||
              _currentTask.status == TaskStatus.inProgress) {
            // Pickup verified - update task status and refresh map for delivery
            _currentTask = _currentTask.copyWith(status: TaskStatus.pickedUp);
            
            // Refresh the map to show delivery route
            setState(() {
              _isLoading = true;
            });
            await _setupMarkersAndRoute();
            setState(() {
              _isLoading = false;
            });
            
            // Show message to proceed to delivery
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Now navigate to delivery location'),
                  backgroundColor: Colors.blue,
                  behavior: SnackBarBehavior.floating,
                  duration: Duration(seconds: 3),
                ),
              );
            }
          } else {
            // Delivery verified - task completed, navigate back to home
            await Future.delayed(const Duration(seconds: 2));
            if (mounted) Navigator.pop(context);
          }
        }
      }
    } catch (e) {
      // Close loading dialog
      if (mounted) Navigator.pop(context);
      
      // Show error
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  String _getActionButtonText() {
    if (_currentTask.status == TaskStatus.assigned ||
        _currentTask.status == TaskStatus.inProgress) {
      return 'Scan Pickup QR';
    }
    return 'Scan Delivery QR';
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Loading Route...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_errorMessage != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text(_errorMessage!),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isLoading = true;
                    _errorMessage = null;
                  });
                  _initializeMap();
                },
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('Task: ${_currentTask.foodType ?? "Delivery"}'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Stack(
        children: [
          // Map or Placeholder
          if (_isMapSupported)
            // Google Map (Android/iOS only)
            GoogleMap(
              initialCameraPosition: CameraPosition(
                target: LatLng(
                  _currentPosition?.latitude ?? 0.0,
                  _currentPosition?.longitude ?? 0.0,
                ),
                zoom: 14,
              ),
              markers: _markers,
              polylines: _polylines,
              myLocationEnabled: true,
              myLocationButtonEnabled: true,
              mapType: MapType.normal,
              onMapCreated: (controller) {
                _mapController = controller;
              },
            )
          else
            // Placeholder for Windows/Web
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Theme.of(context).colorScheme.primary.withOpacity(0.1),
                    Theme.of(context).colorScheme.surface,
                  ],
                ),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.map_outlined,
                      size: 120,
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Map Preview',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Google Maps available on Android/iOS',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Distance: ${widget.task.distanceKm?.toStringAsFixed(2) ?? "N/A"} km',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // Live Tracking Info Card
          if (_distanceToDestination != null || _currentSpeed != null)
            Positioned(
              bottom: 100,
              left: 16,
              right: 16,
              child: Card(
                elevation: 6,
                color: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.blue.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(
                              Icons.navigation,
                              color: Colors.blue,
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'Live Tracking',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildTrackingInfo(
                            icon: Icons.straighten,
                            label: 'Distance',
                            value: _distanceToDestination != null
                                ? '${_distanceToDestination!.toStringAsFixed(2)} km'
                                : '--',
                            color: Colors.green,
                          ),
                          Container(
                            width: 1,
                            height: 40,
                            color: Colors.grey[300],
                          ),
                          _buildTrackingInfo(
                            icon: Icons.speed,
                            label: 'Speed',
                            value: _currentSpeed != null
                                ? '${(_currentSpeed! * 3.6).toStringAsFixed(0)} km/h'
                                : '--',
                            color: Colors.orange,
                          ),
                          Container(
                            width: 1,
                            height: 40,
                            color: Colors.grey[300],
                          ),
                          _buildTrackingInfo(
                            icon: Icons.access_time,
                            label: 'ETA',
                            value: _estimatedTimeArrival ?? '--',
                            color: Colors.purple,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),

          // Task Info Card
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.location_on,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _getDestination().type == 'pickup'
                                ? 'Navigate to Pickup'
                                : 'Navigate to Delivery',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Distance: ${_currentTask.distanceKm?.toStringAsFixed(2) ?? "N/A"} km',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    if (_currentTask.requiresCooling) ...[
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(Icons.ac_unit, size: 16, color: Colors.blue[700]),
                          const SizedBox(width: 4),
                          const Text(
                            'Requires Cooling',
                            style: TextStyle(
                              color: Colors.blue,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openQRScanner,
        icon: const Icon(Icons.qr_code_scanner),
        label: Text(_getActionButtonText()),
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
    );
  }

  Widget _buildTrackingInfo({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
}
