/// Food type enumeration
enum FoodType {
  VEG,
  NON_VEG,
  VEGAN,
  MIXED,
  SNACK;

  /// Get display label for food type
  String get label {
    switch (this) {
      case FoodType.VEG:
        return 'VEG';
      case FoodType.NON_VEG:
        return 'NON-VEG';
      case FoodType.VEGAN:
        return 'VEGAN';
      case FoodType.MIXED:
        return 'MIXED';
      case FoodType.SNACK:
        return 'SNACK';
    }
  }

  /// Parse food type from string
  static FoodType fromString(String value) {
    switch (value.toUpperCase()) {
      case 'VEG':
        return FoodType.VEG;
      case 'NON_VEG':
      case 'NON-VEG':
        return FoodType.NON_VEG;
      case 'VEGAN':
        return FoodType.VEGAN;
      case 'MIXED':
        return FoodType.MIXED;
      case 'SNACK':
        return FoodType.SNACK;
      default:
        return FoodType.MIXED;
    }
  }
}

/// Donation model representing a food donation
class Donation {
  final String id;
  final String donorName;
  final FoodType foodType;
  final double quantity; // in kg
  final String address;
  final DateTime expiryTime;
  final String status;
  final String description;
  final String pickupAddress;
  final DateTime? claimedAt;
  final String? branchName;  // Delivery branch name
  final String? branchAddress;  // Delivery branch address

  Donation({
    required this.id,
    required this.donorName,
    required this.foodType,
    required this.quantity,
    required this.address,
    required this.expiryTime,
    required this.status,
    this.description = '',
    this.pickupAddress = '',
    this.claimedAt,
    this.branchName,
    this.branchAddress,
  });

  /// Create Donation from JSON
  factory Donation.fromJson(Map<String, dynamic> json) {
    return Donation(
      id: json['id']?.toString() ?? '',
      donorName: json['donor_name']?.toString() ?? json['donorName']?.toString() ?? 'Unknown Donor',
      foodType: FoodType.fromString(json['food_type']?.toString() ?? json['foodType']?.toString() ?? 'MIXED'),
      quantity: (json['quantity'] is int) 
          ? (json['quantity'] as int).toDouble() 
          : (json['quantity'] as num?)?.toDouble() ?? 0.0,
      address: json['address']?.toString() ?? json['pickup_address']?.toString() ?? 'Address not provided',
      expiryTime: json['expiry_time'] != null 
          ? DateTime.parse(json['expiry_time'].toString().endsWith('Z') ? json['expiry_time'].toString() : '${json['expiry_time']}Z').toLocal()
          : json['expiryTime'] != null
              ? DateTime.parse(json['expiryTime'].toString().endsWith('Z') ? json['expiryTime'].toString() : '${json['expiryTime']}Z').toLocal()
              : DateTime.now().add(const Duration(hours: 24)),
      status: json['status']?.toString() ?? 'AVAILABLE',
      description: json['description']?.toString() ?? '',
      pickupAddress: json['pickup_address']?.toString() ?? json['address']?.toString() ?? '',
      claimedAt: json['claimed_at'] != null ? DateTime.parse(json['claimed_at'].toString()) : null,
      branchName: json['branch_name']?.toString(),
      branchAddress: json['branch_address']?.toString(),
    );
  }

  /// Convert Donation to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'donor_name': donorName,
      'food_type': foodType.name,
      'quantity': quantity,
      'address': address,
      'pickup_address': pickupAddress,
      'expiry_time': expiryTime.toIso8601String(),
      'status': status,
      'description': description,
      'claimed_at': claimedAt?.toIso8601String(),
    };
  }
}
