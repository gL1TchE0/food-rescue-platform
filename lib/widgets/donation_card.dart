import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/donation_model.dart';

/// Reusable donation card widget
/// Displays donation information and claim button
class DonationCard extends StatelessWidget {
  final Donation donation;
  final VoidCallback onClaim;
  final bool isLoading;

  const DonationCard({
    super.key,
    required this.donation,
    required this.onClaim,
    this.isLoading = false,
  });

  /// Get color for food type badge
  Color _getFoodTypeColor(FoodType foodType) {
    switch (foodType) {
      case FoodType.VEG:
        return Colors.green;
      case FoodType.NON_VEG:
        return Colors.red;
      case FoodType.VEGAN:
        return Colors.teal;
      case FoodType.MIXED:
        return Colors.orange;
      case FoodType.SNACK:
        return Colors.purple;
    }
  }

  /// Format expiry time
  String _formatExpiryTime(DateTime expiryTime) {
    final now = DateTime.now();
    final difference = expiryTime.difference(now);
    
    if (difference.isNegative) {
      return 'Expired';
    } else if (difference.inHours < 1) {
      return 'Expires in ${difference.inMinutes} minutes';
    } else if (difference.inHours < 24) {
      return 'Expires in ${difference.inHours} hours';
    } else {
      return 'Expires on ${DateFormat('MMM dd, hh:mm a').format(expiryTime)}';
    }
  }

  @override
  Widget build(BuildContext context) {
    final expiryText = _formatExpiryTime(donation.expiryTime);
    final isExpired = donation.expiryTime.isBefore(DateTime.now());
    final isExpiringSoon = !isExpired && donation.expiryTime.difference(DateTime.now()).inHours < 2;

    return Card(
      elevation: 3,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header: Donor name and food type badge
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    donation.donorName,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getFoodTypeColor(donation.foodType),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    donation.foodType.label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            
            // Quantity
            Row(
              children: [
                const Icon(Icons.restaurant, size: 20, color: Colors.grey),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Quantity: ${donation.quantity.toStringAsFixed(1)} kg',
                    style: const TextStyle(fontSize: 16),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            // Address
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.location_on, size: 20, color: Colors.grey),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    donation.address,
                    style: const TextStyle(fontSize: 14, color: Colors.black87),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            // Expiry time
            Row(
              children: [
                Icon(
                  Icons.access_time,
                  size: 20,
                  color: isExpiringSoon ? Colors.red : Colors.grey,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    expiryText,
                    style: TextStyle(
                      fontSize: 14,
                      color: isExpiringSoon ? Colors.red : Colors.black87,
                      fontWeight: isExpiringSoon ? FontWeight.bold : FontWeight.normal,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Claim button with hover effects
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: (isLoading || isExpired) ? null : onClaim,
                style: ButtonStyle(
                  backgroundColor: WidgetStateProperty.resolveWith<Color>(
                    (Set<WidgetState> states) {
                      if (isExpired) return Colors.grey;
                      if (states.contains(WidgetState.pressed)) {
                        return const Color(0xFF388E3C); // Darker green when pressed
                      }
                      if (states.contains(WidgetState.hovered)) {
                        return const Color(0xFF66BB6A); // Lighter green on hover
                      }
                      return const Color(0xFF4CAF50); // Default green
                    },
                  ),
                  foregroundColor: WidgetStateProperty.all(Colors.white),
                  padding: WidgetStateProperty.all(
                    const EdgeInsets.symmetric(vertical: 12),
                  ),
                  shape: WidgetStateProperty.all(
                    RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  elevation: WidgetStateProperty.resolveWith<double>(
                    (Set<WidgetState> states) {
                      if (states.contains(WidgetState.hovered)) return 6;
                      if (states.contains(WidgetState.pressed)) return 1;
                      return 2;
                    },
                  ),
                  overlayColor: WidgetStateProperty.all(
                    Colors.white.withOpacity(0.1),
                  ),
                  animationDuration: const Duration(milliseconds: 200),
                ),
                child: isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : Text(
                        isExpired ? 'EXPIRED' : 'CLAIM',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
