import 'package:flutter/material.dart';
import '../models/donation_model.dart';
import '../services/donation_api_service.dart';
import '../widgets/donation_card.dart';
import '../widgets/qr_code_dialog.dart';

/// NGO Claiming Screen
/// Displays available food donations and allows NGOs to claim them
class NgoClaimingScreen extends StatefulWidget {
  final bool showAppBar;
  final VoidCallback? onClaimSuccess;
  
  const NgoClaimingScreen({super.key, this.showAppBar = true, this.onClaimSuccess});

  @override
  State<NgoClaimingScreen> createState() => _NgoClaimingScreenState();
}

class _NgoClaimingScreenState extends State<NgoClaimingScreen> {
  final DonationApiService _apiService = DonationApiService();
  
  List<Donation> _donations = [];
  List<Donation> _filteredDonations = [];
  List<Map<String, dynamic>> _branches = [];
  bool _isLoading = false;
  String? _error;
  String? _claimingDonationId; // Track which donation is being claimed
  String? _selectedFilter; // null = All, or food type name

  @override
  void initState() {
    super.initState();
    _loadDonations();
    _loadBranches();
  }

  /// Apply filter to donations
  void _applyFilter() {
    if (_selectedFilter == null) {
      _filteredDonations = List.from(_donations);
    } else {
      _filteredDonations = _donations
          .where((d) => d.foodType.name == _selectedFilter)
          .toList();
    }
  }

  /// Set the filter
  void _setFilter(String? filter) {
    setState(() {
      _selectedFilter = (_selectedFilter == filter) ? null : filter;
      _applyFilter();
    });
  }

  /// Load branches for the NGO
  Future<void> _loadBranches() async {
    try {
      final branches = await _apiService.getBranches();
      if (mounted) {
        setState(() {
          _branches = branches.where((b) => b['is_active'] == 1).toList();
        });
      }
    } catch (e) {
      print('Error loading branches: $e');
    }
  }

  /// Load available donations from API
  Future<void> _loadDonations() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final donations = await _apiService.getAvailableDonations();
      // Filter out expired donations on the client side as well
      final now = DateTime.now();
      final validDonations = donations.where((d) => d.expiryTime.isAfter(now)).toList();
      setState(() {
        _donations = validDonations;
        _applyFilter();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
      
      // Show error snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading donations: ${e.toString()}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
            action: SnackBarAction(
              label: 'RETRY',
              textColor: Colors.white,
              onPressed: _loadDonations,
            ),
          ),
        );
      }
    }
  }

  /// Claim a donation - show branch selection dialog first
  Future<void> _claimDonation(Donation donation) async {
    // If branches exist, show selection dialog
    if (_branches.isNotEmpty) {
      final selectedBranch = await _showBranchSelectionDialog(donation);
      if (selectedBranch == null) return; // User cancelled
      
      await _performClaim(donation, branchId: selectedBranch['id'] as int);
    } else {
      // No branches, claim directly
      await _performClaim(donation);
    }
  }

  /// Show branch selection dialog
  Future<Map<String, dynamic>?> _showBranchSelectionDialog(Donation donation) async {
    return showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.location_city, color: Color(0xFF4CAF50)),
            SizedBox(width: 8),
            Text('Select Delivery Branch'),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.fastfood, color: Colors.blue.shade700, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '${donation.donorName} - ${donation.quantity} kg',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.blue.shade900,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Where should this donation be delivered?',
                style: TextStyle(fontSize: 13, color: Colors.grey),
              ),
              const SizedBox(height: 12),
              ConstrainedBox(
                constraints: BoxConstraints(
                  maxHeight: MediaQuery.of(context).size.height * 0.4,
                ),
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: _branches.length,
                  itemBuilder: (context, index) {
                    final branch = _branches[index];
                    final capacity = (branch['storage_capacity'] ?? 50.0) as num;
                    final hasCapacity = donation.quantity <= capacity;
                    
                    return Card(
                      elevation: 1,
                      margin: const EdgeInsets.only(bottom: 8),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                        side: BorderSide(
                          color: hasCapacity ? Colors.grey.shade300 : Colors.red.shade200,
                        ),
                      ),
                      child: InkWell(
                        onTap: hasCapacity ? () => Navigator.pop(context, branch) : null,
                        borderRadius: BorderRadius.circular(8),
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: hasCapacity 
                                      ? const Color(0xFF4CAF50).withOpacity(0.1)
                                      : Colors.red.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(
                                  Icons.store,
                                  size: 20,
                                  color: hasCapacity ? const Color(0xFF4CAF50) : Colors.red,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      branch['name'] ?? 'Branch',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: hasCapacity ? Colors.black : Colors.grey,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      branch['address'] ?? '',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey.shade600,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        Icon(
                                          Icons.inventory_2,
                                          size: 12,
                                          color: hasCapacity ? Colors.green : Colors.red,
                                        ),
                                        const SizedBox(width: 4),
                                        Flexible(
                                          child: Text(
                                            'Storage: ${capacity.toStringAsFixed(0)} kg',
                                            style: TextStyle(
                                              fontSize: 11,
                                              color: hasCapacity ? Colors.green : Colors.red,
                                              fontWeight: FontWeight.w500,
                                            ),
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ),
                                        if (!hasCapacity) ...[
                                          const SizedBox(width: 8),
                                          Flexible(
                                            child: Text(
                                              '(Insufficient)',
                                              style: TextStyle(
                                                fontSize: 11,
                                                color: Colors.red.shade700,
                                                fontStyle: FontStyle.italic,
                                              ),
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              if (hasCapacity)
                                const Icon(Icons.chevron_right, color: Colors.grey),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  /// Perform the actual claim operation
  Future<void> _performClaim(Donation donation, {int? branchId}) async {
    setState(() {
      _claimingDonationId = donation.id;
    });

    try {
      final success = await _apiService.claimDonation(donation.id, branchId: branchId);
      
      if (success && mounted) {
        // Show QR code dialog
        await showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => QrCodeDialog(
            donationId: donation.id,
            donorName: donation.donorName,
          ),
        );

        // Remove claimed donation from list
        setState(() {
          _donations.removeWhere((d) => d.id == donation.id);
          _claimingDonationId = null;
        });

        // Notify parent dashboard
        widget.onClaimSuccess?.call();

        // Show success message with option to view cart
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text('✅ Claimed! Added to My Claims'),
              backgroundColor: const Color(0xFF4CAF50),
              duration: const Duration(seconds: 3),
              action: SnackBarAction(
                label: 'VIEW CART',
                textColor: Colors.white,
                onPressed: () {
                  // This will be handled by parent Dashboard
                },
              ),
            ),
          );
        }
      }
    } on Exception catch (e) {
      setState(() {
        _claimingDonationId = null;
      });

      final errorMessage = e.toString().replaceAll('Exception: ', '');
      
      // Check if it's a capacity error
      if (errorMessage.contains('capacity') || errorMessage.contains('exceeds')) {
        _showCapacityExceededDialog(donation, errorMessage);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to claim: $errorMessage'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      }
    }
  }

  /// Show dialog when capacity is exceeded
  void _showCapacityExceededDialog(Donation donation, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        icon: const Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 48),
        title: const Text('Capacity Limit Reached'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Cannot claim this donation',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.orange.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.orange.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.inventory_2, color: Colors.orange.shade700),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'This donation (${donation.quantity} kg) exceeds your NGO\'s capacity limit.',
                      style: TextStyle(color: Colors.orange.shade900),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Try claiming smaller donations or contact admin to increase your capacity.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: widget.showAppBar ? AppBar(
        title: const Text(
          'Available Donations',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF4CAF50),
        foregroundColor: Colors.white,
        elevation: 2,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _loadDonations,
            tooltip: 'Refresh',
          ),
        ],
      ) : null,
      body: RefreshIndicator(
        onRefresh: _loadDonations,
        color: const Color(0xFF4CAF50),
        child: _buildBody(),
      ),
    );
  }

  /// Build filter chip
  Widget _buildFilterChip(String label, String filterValue, Color color, IconData icon) {
    final isSelected = _selectedFilter == filterValue;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: isSelected ? Colors.white : color),
            const SizedBox(width: 4),
            Text(label),
          ],
        ),
        selected: isSelected,
        onSelected: (_) => _setFilter(filterValue),
        selectedColor: color,
        checkmarkColor: Colors.white,
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : Colors.black87,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(color: color.withOpacity(0.5)),
        ),
        elevation: isSelected ? 2 : 0,
      ),
    );
  }

  /// Build the filter bar
  Widget _buildFilterBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.white,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.filter_list, size: 18, color: Colors.grey),
              const SizedBox(width: 8),
              Text(
                'Filter by type:',
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey.shade700,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const Spacer(),
              Text(
                '${_filteredDonations.length} of ${_donations.length}',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip('Veg', 'VEG', Colors.green, Icons.eco),
                _buildFilterChip('Non-Veg', 'NON_VEG', Colors.red, Icons.restaurant),
                _buildFilterChip('Mixed', 'MIXED', Colors.orange, Icons.lunch_dining),
                _buildFilterChip('Snack', 'SNACK', Colors.purple, Icons.cookie),
                _buildFilterChip('Vegan', 'VEGAN', Colors.teal, Icons.spa),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build the main body based on current state
  Widget _buildBody() {
    // Loading state
    if (_isLoading && _donations.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF4CAF50)),
            ),
            SizedBox(height: 16),
            Text(
              'Loading donations...',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    // Error state (only if no donations loaded)
    if (_error != null && _donations.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red.shade300,
              ),
              const SizedBox(height: 16),
              Text(
                'Failed to load donations',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _loadDonations,
                icon: const Icon(Icons.refresh),
                label: const Text('RETRY'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF4CAF50),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
              ),
            ],
          ),
        ),
      );
    }

    // Empty state (no donations at all)
    if (_donations.isEmpty) {
      return ListView(
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.3),
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.inbox_outlined,
                  size: 80,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 16),
                Text(
                  'No donations available',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Pull down to refresh',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade500,
                  ),
                ),
              ],
            ),
          ),
        ],
      );
    }

    // Donation list with filter bar
    return Column(
      children: [
        _buildFilterBar(),
        Expanded(
          child: _filteredDonations.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.filter_alt_off,
                        size: 64,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'No ${_selectedFilter?.toLowerCase().replaceAll('_', '-') ?? ''} donations',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextButton(
                        onPressed: () => _setFilter(null),
                        child: const Text('Clear filter'),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: _filteredDonations.length,
                  itemBuilder: (context, index) {
                    final donation = _filteredDonations[index];
                    final isClaimingThis = _claimingDonationId == donation.id;
                    
                    return DonationCard(
                      donation: donation,
                      onClaim: () => _claimDonation(donation),
                      isLoading: isClaimingThis,
                    );
                  },
                ),
        ),
      ],
    );
  }
}
