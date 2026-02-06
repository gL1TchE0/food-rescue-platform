import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/donation_model.dart';
import '../config/api_config.dart';

/// Service class for donation-related API calls
class DonationApiService {
  /// Get authentication token from storage
  Future<String?> _getToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString('auth_token');
    } catch (e) {
      print('Error getting token: $e');
      return null;
    }
  }

  /// Get headers with authentication token
  Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();
    if (token != null) {
      print('🔐 Adding Authorization header with token: ${token.substring(0, 15)}... (${token.length} chars)');
    } else {
      print('⚠️ No token found for Authorization header');
    }
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  /// Fetch available donations from the API
  /// Returns a list of Donation objects
  /// Throws an exception if the request fails
  Future<List<Donation>> getAvailableDonations() async {
    try {
      final headers = await _getHeaders();
      final url = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.availableDonationsEndpoint}');
      
      print('Fetching donations from: $url');
      
      final response = await http.get(
        url,
        headers: headers,
      ).timeout(ApiConfig.timeout);

      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode == 200) {
        final dynamic jsonData = json.decode(response.body);
        
        // Handle both array and object responses
        List<dynamic> donationsJson;
        if (jsonData is List) {
          donationsJson = jsonData;
        } else if (jsonData is Map && jsonData.containsKey('donations')) {
          donationsJson = jsonData['donations'] as List;
        } else if (jsonData is Map && jsonData.containsKey('data')) {
          donationsJson = jsonData['data'] as List;
        } else {
          throw Exception('Unexpected response format');
        }

        return donationsJson
            .map((json) => Donation.fromJson(json as Map<String, dynamic>))
            .toList();
      } else if (response.statusCode == 401) {
        throw Exception('Unauthorized. Please login again.');
      } else if (response.statusCode == 403) {
        throw Exception('Access forbidden. Only approved NGOs can view donations.');
      } else {
        throw Exception('Failed to load donations: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching donations: $e');
      rethrow;
    }
  }

  /// Claim a donation by updating its status to ASSIGNED
  /// Optionally specify a branch for delivery
  /// Returns true if successful
  /// Throws an exception if the request fails
  Future<bool> claimDonation(String donationId, {int? branchId}) async {
    try {
      final headers = await _getHeaders();
      final url = Uri.parse(
        '${ApiConfig.baseUrl}${ApiConfig.claimDonationEndpoint(donationId)}'
      );
      
      print('Claiming donation at: $url');
      
      final body = {
        'new_status': 'ASSIGNED',
        if (branchId != null) 'branch_id': branchId,
      };
      
      final response = await http.patch(
        url,
        headers: headers,
        body: json.encode(body),
      ).timeout(ApiConfig.timeout);

      print('Claim response status: ${response.statusCode}');
      print('Claim response body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 204) {
        return true;
      } else if (response.statusCode == 400) {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Invalid request');
      } else if (response.statusCode == 401) {
        throw Exception('Unauthorized. Please login again.');
      } else if (response.statusCode == 403) {
        final errorData = json.decode(response.body);
        throw Exception(errorData['detail'] ?? 'Cannot claim this donation. Check capacity limits.');
      } else if (response.statusCode == 404) {
        throw Exception('Donation not found');
      } else {
        throw Exception('Failed to claim donation: ${response.statusCode}');
      }
    } catch (e) {
      print('Error claiming donation: $e');
      rethrow;
    }
  }

  /// Get branches for the current NGO
  Future<List<Map<String, dynamic>>> getBranches() async {
    try {
      final dashboard = await getNgoDashboard();
      return List<Map<String, dynamic>>.from(dashboard['branches'] ?? []);
    } catch (e) {
      print('Error fetching branches: $e');
      return [];
    }
  }

  /// Get NGO info for the current user
  Future<Map<String, dynamic>> getNgoInfo() async {
    try {
      final headers = await _getHeaders();
      final url = Uri.parse('${ApiConfig.baseUrl}/api/auth/ngo');
      
      final response = await http.get(url, headers: headers).timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load NGO info');
      }
    } catch (e) {
      print('Error fetching NGO info: $e');
      rethrow;
    }
  }

  /// Get detailed NGO dashboard data with branches and statistics
  Future<Map<String, dynamic>> getNgoDashboard() async {
    try {
      final headers = await _getHeaders();
      final url = Uri.parse('${ApiConfig.baseUrl}/api/auth/ngo/dashboard');
      
      print('Fetching NGO dashboard from: $url');
      
      final response = await http.get(url, headers: headers).timeout(ApiConfig.timeout);

      print('NGO dashboard response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        throw Exception('Unauthorized. Please login again.');
      } else {
        throw Exception('Failed to load NGO dashboard: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching NGO dashboard: $e');
      rethrow;
    }
  }

  /// Get donations claimed by the current NGO
  Future<List<Donation>> getMyClaimedDonations() async {
    try {
      final headers = await _getHeaders();
      final url = Uri.parse('${ApiConfig.baseUrl}/api/donations/my-claims');
      
      print('Fetching my claims from: $url');
      
      final response = await http.get(url, headers: headers).timeout(ApiConfig.timeout);

      print('My claims response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final List<dynamic> jsonData = json.decode(response.body);
        return jsonData.map((json) => Donation.fromJson(json)).toList();
      } else if (response.statusCode == 401) {
        throw Exception('Unauthorized. Please login again.');
      } else {
        throw Exception('Failed to load claims: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching claims: $e');
      rethrow;
    }
  }

  /// Verify donation pickup/delivery (Change status to COMPLETED)
  Future<Donation> verifyDonationPickup(String donationId) async {
    try {
      final headers = await _getHeaders();
      final url = Uri.parse('${ApiConfig.baseUrl}/api/donations/$donationId/verify');
      
      print('Verifying donation pickup at: $url');
      
      final response = await http.put(url, headers: headers).timeout(ApiConfig.timeout);

      print('Verify response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        return Donation.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to verify donation: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('Error verifying donation: $e');
      rethrow;
    }
  }

  /// Logout - clear saved token
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  /// Save authentication token (for testing purposes)
  /// In production, this should be handled by your authentication flow
  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }
}
