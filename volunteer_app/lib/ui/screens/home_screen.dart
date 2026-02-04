import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:dio/dio.dart';
import 'dart:async';
import '../widgets/slide_to_accept.dart';
import '../../data/location_service.dart';
import '../../data/task_model.dart';
import 'route_screen.dart';

/// Home Screen - Volunteer Status Control
/// Shows "Slide to Online" toggle and map background

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isOnline = false;
  bool _isLoading = false;
  Position? _currentLocation;
  Timer? _taskPollTimer;
  
  // Use the test volunteer ID from backend
  static const String _volunteerId = '9c8f533c-0d1c-453b-98f7-5cd3967afc85';
  final Dio _dio = Dio(BaseOptions(baseUrl: 'http://10.252.76.145:8000/api/v1'));

  final LocationService _locationService = LocationService.instance;

  @override
  void initState() {
    super.initState();
    _initLocation();
    _checkCurrentStatus();
  }

  @override
  void dispose() {
    _taskPollTimer?.cancel();
    super.dispose();
  }

  Future<void> _checkCurrentStatus() async {
    try {
      // Check if volunteer is already online in backend
      final response = await _dio.get(
        '/volunteer/task/current',
        queryParameters: {'volunteer_id': _volunteerId},
      );
      
      // If we get a task, volunteer is online
      if (response.statusCode == 200) {
        setState(() => _isOnline = true);
        _startTaskPolling();
      }
    } catch (e) {
      // 404 is expected if no task, volunteer might be offline or online but no task
      // We'll stay in default OFFLINE state
      print('No current task found');
    }
  }

  Future<void> _initLocation() async {
    try {
      final hasPermission = await _locationService.requestPermission();
      if (!hasPermission) {
        print('Location permission not granted');
        _showError('Location permission is required for this app');
        return;
      }

      final isEnabled = await _locationService.isLocationServiceEnabled();
      if (!isEnabled) {
        print('Location services disabled');
        _showError('Please enable location services in your device settings');
        return;
      }

      final position = await _locationService.getCurrentLocation();
      if (position != null && mounted) {
        setState(() {
          _currentLocation = position;
        });
        print('Initial location: ${position.latitude}, ${position.longitude}');
      } else {
        print('Could not get initial location');
      }
    } catch (e) {
      print('Error initializing location: $e');
      _showError('Failed to initialize location: $e');
    }
  }

  void _showError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  Future<void> _toggleOnlineStatus() async {
    setState(() => _isLoading = true);

    try {
      if (!_isOnline) {
        // Going ONLINE
        // Check permissions first
        final hasPermission = await _locationService.requestPermission();
        if (!hasPermission) {
          setState(() => _isLoading = false);
          _showError('Location permission is required. Please grant location access in app settings.');
          return;
        }

        final isEnabled = await _locationService.isLocationServiceEnabled();
        if (!isEnabled) {
          setState(() => _isLoading = false);
          _showError('Location services are disabled. Please enable them in device settings.');
          return;
        }

        // Get fresh location
        final position = await _locationService.getCurrentLocation();
        if (position == null) {
          setState(() => _isLoading = false);
          _showError('Could not get your current location. Please check location settings.');
          return;
        }
        
        setState(() => _currentLocation = position);

        // 1. Update location first
        print('Updating location: ${position.latitude}, ${position.longitude}');
        final locationResponse = await _dio.post(
          '/volunteer/location',
          queryParameters: {'volunteer_id': _volunteerId},
          data: {
            'lat': position.latitude,
            'lng': position.longitude,
            'speed': 0.0,
            'heading': 0.0,
          },
        );
        print('Location updated: ${locationResponse.statusCode}');

        // 2. Update status to ONLINE (skip if already online)
        print('Updating status to ONLINE');
        try {
          final statusResponse = await _dio.post(
            '/volunteer/status',
            queryParameters: {'volunteer_id': _volunteerId},
            data: {'status': 'ONLINE'},
          );
          print('Status updated: ${statusResponse.statusCode}');
        } catch (e) {
          if (e is DioException && e.response?.data['detail']?.contains('Invalid transition') == true) {
            print('Volunteer already ONLINE, continuing...');
          } else {
            rethrow;
          }
        }

        // 3. Start polling for tasks
        _startTaskPolling();
      } else {
        // Going OFFLINE
        print('Updating status to OFFLINE');
        await _dio.post(
          '/volunteer/status',
          queryParameters: {'volunteer_id': _volunteerId},
          data: {'status': 'OFFLINE'},
        );

        // Stop polling
        _taskPollTimer?.cancel();
      }

      setState(() {
        _isOnline = !_isOnline;
        _isLoading = false;
      });

      // Show confirmation
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_isOnline ? 'You are now ONLINE ✓' : 'You are now OFFLINE'),
            backgroundColor: _isOnline ? Colors.green : Colors.grey,
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      print('Error toggling status: $e');
      if (e is DioException) {
        print('Response: ${e.response?.data}');
        print('Status code: ${e.response?.statusCode}');
      }
      
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    }
  }

  void _startTaskPolling() {
    _taskPollTimer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      try {
        final response = await _dio.get(
          '/volunteer/task/current',
          queryParameters: {'volunteer_id': _volunteerId},
        );

        if (response.statusCode == 200 && response.data != null) {
          // Task found! Navigate to route screen
          timer.cancel();
          if (mounted) {
            final task = Task.fromJson(response.data);
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (context) => RouteScreen(task: task),
              ),
            );
          }
        }
      } catch (e) {
        // 404 means no task yet, keep polling
        if (e is DioException && e.response?.statusCode == 404) {
          // Expected, continue polling
        } else {
          print('Error polling for tasks: $e');
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Blurred Map Background
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
              child: Icon(
                Icons.map_outlined,
                size: 200,
                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
              ),
            ),
          ),

          // Status Overlay
          SafeArea(
            child: Column(
              children: [
                // Header
                Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'M7 Volunteer',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Container(
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  color: _isOnline ? Colors.green : Colors.grey,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _isOnline ? 'ONLINE' : 'OFFLINE',
                                style: TextStyle(
                                  color: _isOnline ? Colors.green : Colors.grey,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      IconButton(
                        icon: const Icon(Icons.person_outline),
                        onPressed: () {
                          // Navigate to profile
                        },
                      ),
                    ],
                  ),
                ),

                const Spacer(),

                // Main Status Card
                if (!_isOnline)
                  Container(
                    margin: const EdgeInsets.all(20),
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surface,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.05),
                          blurRadius: 20,
                          offset: const Offset(0, 10),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        Icon(
                          Icons.volunteer_activism,
                          size: 64,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Ready to help?',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Slide below to go online and start accepting tasks',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                          ),
                        ),
                      ],
                    ),
                  ),

                if (_isOnline)
                  Container(
                    margin: const EdgeInsets.all(20),
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.green, width: 2),
                    ),
                    child: Column(
                      children: [
                        const Icon(
                          Icons.check_circle,
                          size: 64,
                          color: Colors.green,
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'You\'re Online!',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Waiting for task assignment...',
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                          ),
                        ),
                        const SizedBox(height: 16),
                        const CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.green),
                        ),
                      ],
                    ),
                  ),

                // Slide to Online Toggle
                SlideToAccept(
                  text: _isOnline ? 'Slide to go OFFLINE' : 'Slide to go ONLINE',
                  backgroundColor: _isOnline ? Colors.grey.shade200 : Colors.green.shade50,
                  foregroundColor: _isOnline ? Colors.grey : Colors.green,
                  icon: _isOnline ? Icons.power_settings_new : Icons.check,
                  onConfirm: _toggleOnlineStatus,
                  isLoading: _isLoading,
                ),

                const SizedBox(height: 40),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
