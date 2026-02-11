import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// API Service for communicating with unified backend
class ApiService {
  // Using LAN IP for physical device testing
  static const String baseUrl = 'http://localhost:8000/api/v1'; // Emulator only
  //static const String baseUrl = 'http://10.186.157.145:8000/api/v1'; // Physical Device LAN IP
  
  late final Dio _dio;
  String? _authToken;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_authToken != null) {
          options.headers['Authorization'] = 'Bearer $_authToken';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        // Handle 401 Unauthorized
        if (error.response?.statusCode == 401) {
          // Token expired, redirect to login
          clearToken();
        }
        // Handle 403 Forbidden - Log details
        if (error.response?.statusCode == 403) {
          print('403 Forbidden: ${error.response?.data}');
        }
        return handler.next(error);
      },
    ));
  }

  /// Set auth token
  Future<void> setToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  /// Load token from storage
  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
  }

  /// Clear token on logout
  Future<void> clearToken() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  bool get isAuthenticated => _authToken != null;

  // ==================== AUTH ENDPOINTS ====================

  /// Register new user
  Future<Map<String, dynamic>> register({
    required String email,
    required String fullName,
    required String phoneNumber,
    required String role,
  }) async {
    final response = await _dio.post('/auth/register', data: {
      'email': email,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'role': role.toUpperCase(), // Backend expects uppercase: DONOR, VOLUNTEER, NGO, ADMIN
      'clerk_user_id': 'mobile_${email.replaceAll('@', '_').replaceAll('.', '_')}', // Generate simple ID for test mode
    });
    return response.data;
  }

  /// Login (test mode)
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _dio.post('/auth/login',
        data: {'username': email, 'password': password},
        options: Options(contentType: Headers.formUrlEncodedContentType));
    
    if (response.data['access_token'] != null) {
      await setToken(response.data['access_token']);
    }
    return response.data;
  }

  /// Get current user profile
  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/auth/me');
    return response.data;
  }

  // ==================== DONOR ENDPOINTS ====================

  /// Get donor profile
  Future<Map<String, dynamic>> getDonorProfile() async {
    final response = await _dio.get('/donors/me');
    return response.data;
  }

  /// Create donor profile
  Future<Map<String, dynamic>> createDonorProfile({
    required String organizationName,
    required String address,
    required double latitude,
    required double longitude,
  }) async {
    final response = await _dio.post('/donors', data: {
      'organization_name': organizationName,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
    });
    return response.data;
  }

  /// Get donor's tasks
  Future<List<dynamic>> getDonorTasks() async {
    final response = await _dio.get('/donors/tasks');
    return response.data;
  }

  /// Create donation task
  Future<Map<String, dynamic>> createDonation({
    required double pickupLat,
    required double pickupLng,
    double? dropLat,
    double? dropLng,
    required String foodType,
    required double quantityKg,
    String? description,
    bool requiresCooling = false,
    DateTime? expiryTime,
  }) async {
    final response = await _dio.post('/donors/tasks', data: {
      'pickup_lat': pickupLat,
      'pickup_lng': pickupLng,
      'drop_lat': dropLat,
      'drop_lng': dropLng,
      'food_type': foodType,
      'quantity_kg': quantityKg,
      'description': description,
      'requires_cooling': requiresCooling,
      'expiry_time': expiryTime?.toIso8601String(),
    });
    return response.data;
  }

  // ==================== NGO ENDPOINTS ====================

  /// Get NGO profile
  Future<Map<String, dynamic>> getNgoProfile() async {
    final response = await _dio.get('/ngos/me');
    return response.data;
  }

  /// Create NGO profile
  Future<Map<String, dynamic>> createNgoProfile({
    required String organizationName,
    required String licenseNumber,
    required String address,
    required double latitude,
    required double longitude,
    int capacityKg = 100,
  }) async {
    final response = await _dio.post('/ngos', data: {
      'organization_name': organizationName,
      'license_number': licenseNumber,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
      'capacity_kg': capacityKg,
    });
    return response.data;
  }

  /// Get nearby tasks for NGO
  Future<List<dynamic>> getNgoNearbyTasks() async {
    final response = await _dio.get('/ngos/nearby-tasks');
    return response.data;
  }

  /// Claim a task
  Future<Map<String, dynamic>> claimTask(String taskId) async {
    final response = await _dio.post('/ngos/tasks/$taskId/claim');
    return response.data;
  }

  /// Get claimed tasks
  Future<List<dynamic>> getNgoClaimedTasks() async {
    final response = await _dio.get('/ngos/claimed-tasks');
    return response.data;
  }
  
  /// Verify receipt of a task (complete it)
  Future<Map<String, dynamic>> verifyTaskReceipt(String taskId) async {
    final response = await _dio.post('/ngos/tasks/$taskId/verify');
    return response.data;
  }

  // ==================== VOLUNTEER ENDPOINTS ====================

  /// Get volunteer profile
  Future<Map<String, dynamic>> getVolunteerProfile() async {
    final response = await _dio.get('/volunteers/me');
    return response.data;
  }

  /// Create volunteer profile
  Future<Map<String, dynamic>> createVolunteerProfile({
    required String vehicleType,
    required bool hasCooling,
    required double capacityKg,
  }) async {
    final response = await _dio.post('/volunteers', data: {
      'vehicle_type': vehicleType,
      'has_cooling': hasCooling,
      'capacity_kg': capacityKg,
    });
    return response.data;
  }

  /// Go online
  Future<Map<String, dynamic>> goOnline(double lat, double lng) async {
    final response = await _dio.post('/volunteers/go-online', queryParameters: {
      'latitude': lat,
      'longitude': lng,
    });
    return response.data;
  }

  /// Go offline
  Future<Map<String, dynamic>> goOffline() async {
    try {
      final response = await _dio.post('/volunteers/go-offline');
      return response.data;
    } catch (e) {
      // If unauthorized (401), we might already be logged out or token expired
      // Just return empty success to allow local logout to proceed
      return {'status': 'success', 'message': 'Forced offline locally'};
    }
  }

  /// Update location
  Future<Map<String, dynamic>> updateLocation(double lat, double lng) async {
    final response = await _dio.patch('/volunteers/location', data: {
      'latitude': lat,
      'longitude': lng,
    });
    return response.data;
  }

  /// Get current task
  Future<Map<String, dynamic>?> getCurrentTask() async {
    try {
      final response = await _dio.get('/volunteers/current-task');
      return response.data;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      rethrow;
    }
  }

  /// Accept task
  Future<Map<String, dynamic>> acceptTask(String taskId) async {
    final response = await _dio.post('/tasks/$taskId/accept');
    return response.data;
  }

  /// Verify pickup with QR token
  Future<Map<String, dynamic>> verifyPickup(String taskId, String qrToken) async {
    final response = await _dio.post('/tasks/$taskId/pickup-verify', data: {
      'token': qrToken, // Backend expects 'token', not 'qr_token' in QRVerifyRequest
    });
    return response.data;
  }

  /// Verify delivery with QR token
  Future<Map<String, dynamic>> verifyDelivery(String taskId, String qrToken) async {
    final response = await _dio.post('/tasks/$taskId/delivery-verify', data: {
      'token': qrToken, // Backend expects 'token', not 'qr_token'
    });
    return response.data;
  }

  /// Get task history
  Future<List<dynamic>> getTaskHistory() async {
    final response = await _dio.get('/volunteers/task-history');
    return response.data;
  }
}
