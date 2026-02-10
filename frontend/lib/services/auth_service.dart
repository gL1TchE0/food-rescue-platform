// lib/services/auth_service.dart

import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

class AuthService {
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000';
    } else if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    } else {
      return 'http://localhost:8000';
    }
  }

  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'auth_user';
  static const Duration _timeout = Duration(seconds: 10);

  // =========================================================================
  // TOKEN MANAGEMENT
  // =========================================================================

  /// Save token and user to local storage
  Future<void> saveAuthData(AuthToken authToken) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, authToken.accessToken);
    await prefs.setString(_userKey, json.encode(authToken.user.toJson()));
  }

  /// Get saved token
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  /// Get saved user
  Future<User?> getSavedUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_userKey);
    if (userJson != null) {
      return User.fromJson(json.decode(userJson));
    }
    return null;
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  /// Clear auth data (logout)
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }

  // =========================================================================
  // AUTH API CALLS
  // =========================================================================

  /// Register new user
  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String phone,
    required String password,
    required UserRole role,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'name': name,
          'email': email,
          'phone': phone,
          'password': password,
          'role': role.value,
        }),
      ).timeout(_timeout);

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message'], 'email': data['email']};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Registration failed'};
      }
    } on TimeoutException {
      return {'success': false, 'message': 'Connection timed out. Please check your internet and try again.'};
    } on SocketException {
      return {'success': false, 'message': 'Cannot reach the server. Please check your connection.'};
    } catch (e) {
      return {'success': false, 'message': 'Something went wrong. Please try again.'};
    }
  }

  /// Verify OTP after registration
  Future<Map<String, dynamic>> verifyOtp({
    required String email,
    required String otp,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/verify-otp'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'otp': otp,
        }),
      ).timeout(_timeout);

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        final authToken = AuthToken.fromJson(data);
        await saveAuthData(authToken);
        return {'success': true, 'user': authToken.user};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'OTP verification failed'};
      }
    } on TimeoutException {
      return {'success': false, 'message': 'Connection timed out. Please try again.'};
    } on SocketException {
      return {'success': false, 'message': 'Cannot reach the server. Please check your connection.'};
    } catch (e) {
      return {'success': false, 'message': 'Something went wrong. Please try again.'};
    }
  }

  /// Login step 1 - send credentials
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      ).timeout(_timeout);

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message'], 'email': data['email']};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Login failed'};
      }
    } on TimeoutException {
      return {'success': false, 'message': 'Connection timed out. Please check your internet and try again.'};
    } on SocketException {
      return {'success': false, 'message': 'Cannot reach the server. Please check your connection.'};
    } catch (e) {
      return {'success': false, 'message': 'Something went wrong. Please try again.'};
    }
  }

  /// Login step 2 - verify OTP
  Future<Map<String, dynamic>> loginVerify({
    required String email,
    required String otp,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login/verify'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'otp': otp,
        }),
      ).timeout(_timeout);

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        final authToken = AuthToken.fromJson(data);
        await saveAuthData(authToken);
        return {'success': true, 'user': authToken.user};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'OTP verification failed'};
      }
    } on TimeoutException {
      return {'success': false, 'message': 'Connection timed out. Please try again.'};
    } on SocketException {
      return {'success': false, 'message': 'Cannot reach the server. Please check your connection.'};
    } catch (e) {
      return {'success': false, 'message': 'Something went wrong. Please try again.'};
    }
  }

  /// Resend OTP
  Future<Map<String, dynamic>> resendOtp({required String email}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/resend-otp'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email}),
      ).timeout(_timeout);

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message']};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Failed to resend OTP'};
      }
    } on TimeoutException {
      return {'success': false, 'message': 'Connection timed out. Please try again.'};
    } on SocketException {
      return {'success': false, 'message': 'Cannot reach the server. Please check your connection.'};
    } catch (e) {
      return {'success': false, 'message': 'Something went wrong. Please try again.'};
    }
  }
}
