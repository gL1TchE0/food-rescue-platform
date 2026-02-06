import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/donation_model.dart';
import '../services/donation_api_service.dart';
import '../widgets/claimed_donation_card.dart';
import '../widgets/qr_code_dialog.dart';

/// Screen showing all donations claimed by the current NGO
/// Acts like a cart/order history
class MyClaimsScreen extends StatefulWidget {
  const MyClaimsScreen({super.key});

  @override
  State<MyClaimsScreen> createState() => MyClaimsScreenState();
}

class MyClaimsScreenState extends State<MyClaimsScreen> {
  final DonationApiService _apiService = DonationApiService();
  List<Donation> _claimedDonations = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadClaimedDonations();
  }

  /// Public method to refresh claims from outside
  void refresh() {
    _loadClaimedDonations();
  }

  Future<void> _loadClaimedDonations() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final donations = await _apiService.getMyClaimedDonations();
      if (mounted) {
        setState(() {
          _claimedDonations = donations;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          Container(
            color: Colors.white,
            child: const TabBar(
              labelColor: Color(0xFF4CAF50),
              unselectedLabelColor: Colors.grey,
              indicatorColor: Color(0xFF4CAF50),
              tabs: [
                Tab(text: 'ACTIVE'),
                Tab(text: 'HISTORY'),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              children: [
                _buildList(active: true),
                _buildList(active: false),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildList({required bool active}) {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Color(0xFF4CAF50)),
            SizedBox(height: 16),
            Text('Loading your claims...'),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text(
                'Failed to load claims',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _loadClaimedDonations,
                icon: const Icon(Icons.refresh),
                label: const Text('RETRY'),
              ),
            ],
          ),
        ),
      );
    }

    // Filter donations based on tab
    final filteredDonations = _claimedDonations.where((d) {
      final isCompleted = d.status == 'COMPLETED' || d.status == 'DELIVERED';
      return active ? !isCompleted : isCompleted;
    }).toList();

    if (filteredDonations.isEmpty) {
      return RefreshIndicator(
        onRefresh: _loadClaimedDonations,
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            SizedBox(height: MediaQuery.of(context).size.height * 0.1),
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    active ? Icons.shopping_basket_outlined : Icons.history,
                    size: 80,
                    color: Colors.grey.shade400,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    active ? 'No Active Claims' : 'No History Yet',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    active
                        ? 'Claim donations from the Available tab\nto see them here'
                        : 'Completed pickups will appear here',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey.shade500),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadClaimedDonations,
      child: Column(
        children: [
          // Show summary only on Active tab or adjust as needed
          if (active) _buildMonthlySummary(filteredDonations),

          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              itemCount: filteredDonations.length,
              itemBuilder: (context, index) {
                final donation = filteredDonations[index];
                return ClaimedDonationCard(
                  donation: donation,
                  // Show QR only for Active tab
                  onShowQr: active ? () => _showQrCode(donation, active) : null,
                  // Show time for both Active and History
                  showTime: true,
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMonthlySummary(List<Donation> donations) {
    // Filter claims for current month and year from the passed list
    final now = DateTime.now();
    final monthlyClaims = donations.where((d) {
      if (d.claimedAt == null) return false;
      return d.claimedAt!.month == now.month && d.claimedAt!.year == now.year;
    }).toList();

    // If no claims this month in this view, don't show summary to avoid clutter or show 0
    // showing it is fine.

    final monthName = DateFormat('MMMM yyyy').format(now);
    final totalQuantity =
        monthlyClaims.fold<double>(0, (sum, d) => sum + d.quantity);

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF4CAF50), Color(0xFF66BB6A)],
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.green.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Month Header
          Row(
            children: [
              const Icon(Icons.calendar_month, color: Colors.white70, size: 16),
              const SizedBox(width: 8),
              Text(
                'Active Claims Overview ($monthName)',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const Divider(color: Colors.white24, height: 24),
          Row(
            children: [
              const Icon(Icons.inventory_2, color: Colors.white, size: 40),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Claims',
                      style: TextStyle(color: Colors.white70, fontSize: 13),
                    ),
                    Text(
                      '${monthlyClaims.length}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  const Text(
                    'To Collect',
                    style: TextStyle(color: Colors.white70, fontSize: 13),
                  ),
                  Text(
                    '${totalQuantity.toStringAsFixed(1)} kg',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showQrCode(Donation donation, bool isActive) {
    // Import QrCodeDialog if needed, assuming it's imported via previous import
    showDialog(
      context: context,
      builder: (context) => QrCodeDialog(
        donationId: donation.id,
        donorName: donation.donorName,
        onVerify: isActive ? () => _verifyDonation(donation.id) : null,
      ),
    );
  }

  Future<void> _verifyDonation(String donationId) async {
    try {
      await _apiService.verifyDonationPickup(donationId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Verification Successful! Moved to History.'),
          backgroundColor: Colors.green,
        ));
      }
      _loadClaimedDonations(); // Refresh list to move it
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Verification failed: $e'),
          backgroundColor: Colors.red,
        ));
      }
    }
  }
}
