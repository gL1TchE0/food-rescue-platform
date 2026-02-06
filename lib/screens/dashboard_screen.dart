import 'package:flutter/material.dart';
import 'ngo_claiming_screen.dart';
import 'my_claims_screen.dart';
import 'ngo_profile_screen.dart';
import '../services/donation_api_service.dart';

/// Main dashboard with bottom navigation
/// Tabs: Available Donations | My Claims | Profile
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;
  String _ngoName = 'Loading...';
  int _claimsCount = 0;
  final DonationApiService _apiService = DonationApiService();
  final GlobalKey<MyClaimsScreenState> _myClaimsKey = GlobalKey<MyClaimsScreenState>();

  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _screens = [
      NgoClaimingScreen(showAppBar: false, onClaimSuccess: _onClaimSuccess),
      MyClaimsScreen(key: _myClaimsKey),
      const NgoProfileScreen(),
    ];
    _loadNgoInfo();
    _loadClaimsCount();
  }

  /// Called when a donation is successfully claimed
  void _onClaimSuccess() {
    _loadClaimsCount();
    // Refresh the My Claims screen
    _myClaimsKey.currentState?.refresh();
  }

  Future<void> _loadClaimsCount() async {
    try {
      final claims = await _apiService.getMyClaimedDonations();
      if (mounted) {
        setState(() {
          _claimsCount = claims.length;
        });
      }
    } catch (e) {
      print('Error loading claims count: $e');
    }
  }

  Future<void> _loadNgoInfo() async {
    try {
      final ngoInfo = await _apiService.getNgoInfo();
      if (mounted) {
        setState(() {
          _ngoName = ngoInfo['name'] ?? 'NGO Dashboard';
        });
      }
    } catch (e) {
      print('Error loading NGO info: $e');
      if (mounted) {
        setState(() {
          _ngoName = 'Food Rescue NGO';
        });
      }
    }
  }

  String _getSubtitle() {
    switch (_currentIndex) {
      case 0:
        return 'Available Donations';
      case 1:
        return 'My Claims';
      case 2:
        return 'NGO Profile';
      default:
        return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _ngoName,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              _getSubtitle(),
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {});
            },
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _showLogoutDialog(),
            tooltip: 'Logout',
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
          if (index == 1) {
            _loadClaimsCount(); // Refresh count when switching to claims
            _myClaimsKey.currentState?.refresh(); // Refresh the claims list
          }
        },
        destinations: [
          const NavigationDestination(
            icon: Icon(Icons.restaurant_menu_outlined),
            selectedIcon: Icon(Icons.restaurant_menu),
            label: 'Available',
          ),
          NavigationDestination(
            icon: Badge(
              isLabelVisible: _claimsCount > 0,
              label: Text('$_claimsCount'),
              child: const Icon(Icons.shopping_cart_outlined),
            ),
            selectedIcon: Badge(
              isLabelVisible: _claimsCount > 0,
              label: Text('$_claimsCount'),
              child: const Icon(Icons.shopping_cart),
            ),
            label: 'My Claims',
          ),
          const NavigationDestination(
            icon: Icon(Icons.business_outlined),
            selectedIcon: Icon(Icons.business),
            label: 'Profile',
          ),
        ],
      ),
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              await _apiService.logout();
              if (mounted) {
                Navigator.pop(context);
                // Show logged out message
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Logged out successfully')),
                );
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}
