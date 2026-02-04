import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:async';

/// Location Service for GPS Tracking
/// Streams location updates every 5 seconds during active tasks

class LocationService {
  static final LocationService instance = LocationService._();
  LocationService._();

  StreamSubscription<Position>? _positionStreamSubscription;
  Stream<Position>? _positionStream;

  /// Request location permissions
  Future<bool> requestPermission() async {
    var status = await Permission.location.status;
    
    if (status.isDenied) {
      status = await Permission.location.request();
    }

    if (status.isPermanentlyDenied) {
      await openAppSettings();
      return false;
    }

    return status.isGranted;
  }

  /// Check if location service is enabled
  Future<bool> isLocationServiceEnabled() async {
    return await Geolocator.isLocationServiceEnabled();
  }

  /// Get current location once
  Future<Position?> getCurrentLocation() async {
    try {
      final hasPermission = await requestPermission();
      if (!hasPermission) return null;

      final isEnabled = await isLocationServiceEnabled();
      if (!isEnabled) return null;

      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
    } catch (e) {
      print('Error getting location: $e');
      return null;
    }
  }

  /// Start streaming location updates
  /// Used during NAVIGATING and IN_TRANSIT states
  Stream<Position> startLocationStream() {
    _positionStream ??= Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10, // Update every 10 meters
        timeLimit: Duration(seconds: 5),
      ),
    );

    return _positionStream!;
  }

  /// Subscribe to location updates
  void startTracking(Function(Position) onLocationUpdate) {
    _positionStreamSubscription = startLocationStream().listen(
      onLocationUpdate,
      onError: (error) {
        print('Location stream error: $error');
      },
    );
  }

  /// Stop location tracking
  void stopTracking() {
    _positionStreamSubscription?.cancel();
    _positionStreamSubscription = null;
  }

  /// Calculate distance between two points (in meters)
  double calculateDistance(
    double startLat,
    double startLng,
    double endLat,
    double endLng,
  ) {
    return Geolocator.distanceBetween(startLat, startLng, endLat, endLng);
  }

  /// Calculate bearing (direction) between two points
  double calculateBearing(
    double startLat,
    double startLng,
    double endLat,
    double endLng,
  ) {
    return Geolocator.bearingBetween(startLat, startLng, endLat, endLng);
  }
}
