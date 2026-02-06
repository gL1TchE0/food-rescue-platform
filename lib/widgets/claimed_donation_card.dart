import 'package:flutter/material.dart';
import '../models/donation_model.dart';

/// Card widget for displaying claimed donations
/// Shows donation info with status and QR code option
class ClaimedDonationCard extends StatelessWidget {
  final Donation donation;
  final VoidCallback? onShowQr;
  final bool showTime;

  const ClaimedDonationCard({
    super.key,
    required this.donation,
    this.onShowQr,
    this.showTime = true,
  });

  Color _getFoodTypeColor(FoodType type) {
    switch (type) {
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

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Row
            Row(
              children: [
                // Food Type Badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getFoodTypeColor(donation.foodType),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    donation.foodType.label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                // Custom Status
                const Text(
                   '✅ Successfully Received',
                   style: TextStyle(
                     fontSize: 11,
                     fontWeight: FontWeight.bold,
                     color: Colors.green, // Visual feedback for success
                   ),
                ),
                const Spacer(),
                // Quantity
                Text(
                  '${donation.quantity} kg',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF4CAF50),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Address (Pickup Location)
            Row(
              children: [
                const Icon(Icons.location_on, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    'Pickup: ${donation.pickupAddress}',
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),

            // Delivery Branch Location
            if (donation.branchName != null)
              Row(
                children: [
                  const Icon(Icons.local_shipping, size: 16, color: Color(0xFF4CAF50)),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      'Deliver to: ${donation.branchName}${donation.branchAddress != null ? ' - ${donation.branchAddress}' : ''}',
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF4CAF50),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            const SizedBox(height: 8),

            // Description
            if (donation.description.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  donation.description,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade700,
                  ),
                ),
              ),

            const SizedBox(height: 12),

            // Time & QR Button
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                if (showTime)
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                         const Text(
                          '🕒 Time of collection',
                          style: TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                        Text(
                          _formatDate(donation.claimedAt),
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade800,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                if (!showTime) const Spacer(), // Push QR button to right if time is hidden
                
                if (onShowQr != null) ...[
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: onShowQr,
                    icon: const Icon(Icons.qr_code, size: 18),
                    label: const Text('Show QR'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4CAF50),
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap, // Reduces minimum size constraints
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'assigned':
        return Colors.blue;
      case 'picked_up':
        return Colors.purple;
      case 'delivered':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  String _formatDate(DateTime? date) {
    if (date == null) return 'N/A';
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
