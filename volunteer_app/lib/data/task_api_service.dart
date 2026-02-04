import 'package:dio/dio.dart';
import 'task_model.dart';

/// API Service for Task-related operations
/// Handles communication with the backend API
class TaskApiService {
  static const String baseUrl = 'http://10.252.76.145:8000/api/v1';
  final Dio _dio;

  TaskApiService() : _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {
      'Content-Type': 'application/json',
    },
  ));

  /// Verify pickup with QR token
  /// 
  /// Transitions task from ASSIGNED -> IN_TRANSIT
  /// Returns true if verification successful
  Future<bool> verifyPickup(String taskId, String qrToken) async {
    try {
      final response = await _dio.post(
        '/task/$taskId/verify-pickup',
        data: {
          'qr_token': qrToken,
        },
      );

      if (response.statusCode == 200) {
        return response.data['status'] == 'success';
      }
      return false;
    } on DioException catch (e) {
      print('Error verifying pickup: ${e.message}');
      if (e.response != null) {
        print('Response data: ${e.response?.data}');
      }
      rethrow;
    }
  }

  /// Verify delivery with QR token
  /// 
  /// Transitions task from IN_TRANSIT -> DELIVERED -> COMPLETED
  /// Returns true if verification successful
  Future<bool> verifyDelivery(String taskId, String qrToken) async {
    try {
      final response = await _dio.post(
        '/task/$taskId/verify-dropoff',
        data: {
          'qr_token': qrToken,
        },
      );

      if (response.statusCode == 200) {
        return response.data['status'] == 'success';
      }
      return false;
    } on DioException catch (e) {
      print('Error verifying delivery: ${e.message}');
      if (e.response != null) {
        print('Response data: ${e.response?.data}');
      }
      rethrow;
    }
  }

  /// Get task details by ID
  Future<Task?> getTask(String taskId) async {
    try {
      final response = await _dio.get('/task/$taskId');
      
      if (response.statusCode == 200) {
        return Task.fromJson(response.data);
      }
      return null;
    } on DioException catch (e) {
      print('Error fetching task: ${e.message}');
      return null;
    }
  }

  /// Accept a task assignment
  Future<bool> acceptTask(String taskId, String volunteerId) async {
    try {
      final response = await _dio.post(
        '/task/$taskId/accept',
        data: {
          'volunteer_id': volunteerId,
        },
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error accepting task: ${e.message}');
      return false;
    }
  }

  /// Report an exception/issue with the task
  Future<bool> reportException(
    String taskId,
    String issueType,
    String? description,
  ) async {
    try {
      final response = await _dio.post(
        '/task/$taskId/exception',
        data: {
          'issue_type': issueType,
          'description': description,
        },
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error reporting exception: ${e.message}');
      return false;
    }
  }
}
