/// API Configuration
/// Update the baseUrl to match your FastAPI backend URL
class ApiConfig {
  // TODO: Update this to your actual backend URL
  // For local development: 'http://10.0.2.2:8000' (Android emulator)
  // For local development: 'http://localhost:8000' (iOS simulator)
  // For physical device: Use your computer's local IP
  // For production: 'https://your-api.com'
  static const String baseUrl = 'http://10.129.153.207:8000';
  
  // API Endpoints
  static const String availableDonationsEndpoint = '/api/donations/available';
  static String claimDonationEndpoint(String id) => '/api/donations/$id/status';
  
  // Request timeout
  static const Duration timeout = Duration(seconds: 30);
}
