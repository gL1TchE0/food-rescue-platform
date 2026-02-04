/// Task Model
/// Represents a delivery task assigned to a volunteer
class Task {
  final String id;
  final String donorId;
  final String ngoId;
  final String? volunteerId;
  final Location pickupLocation;
  final Location dropLocation;
  final double? distanceKm;
  final String? foodType;
  final DateTime expiryTime;
  final bool requiresCooling;
  final TaskStatus status;
  final String? pickupToken;
  final String? deliveryToken;
  final DateTime createdAt;
  final DateTime? completedAt;

  Task({
    required this.id,
    required this.donorId,
    required this.ngoId,
    this.volunteerId,
    required this.pickupLocation,
    required this.dropLocation,
    this.distanceKm,
    this.foodType,
    required this.expiryTime,
    required this.requiresCooling,
    required this.status,
    this.pickupToken,
    this.deliveryToken,
    required this.createdAt,
    this.completedAt,
  });

  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'],
      donorId: json['donor_id'],
      ngoId: json['ngo_id'],
      volunteerId: json['volunteer_id'],
      pickupLocation: Location(
        lat: json['pickup_lat'] ?? 0.0,
        lng: json['pickup_lng'] ?? 0.0,
      ),
      dropLocation: Location(
        lat: json['drop_lat'] ?? 0.0,
        lng: json['drop_lng'] ?? 0.0,
      ),
      distanceKm: json['distance_km']?.toDouble(),
      foodType: json['food_type'],
      expiryTime: DateTime.parse(json['expiry_time']),
      requiresCooling: json['requires_cooling'] ?? false,
      status: TaskStatus.fromString(json['status']),
      pickupToken: json['pickup_token'],
      deliveryToken: json['delivery_token'],
      createdAt: DateTime.parse(json['created_at']),
      completedAt: json['completed_at'] != null 
          ? DateTime.parse(json['completed_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'donor_id': donorId,
      'ngo_id': ngoId,
      'volunteer_id': volunteerId,
      'pickup_lat': pickupLocation.lat,
      'pickup_lng': pickupLocation.lng,
      'drop_lat': dropLocation.lat,
      'drop_lng': dropLocation.lng,
      'distance_km': distanceKm,
      'food_type': foodType,
      'expiry_time': expiryTime.toIso8601String(),
      'requires_cooling': requiresCooling,
      'status': status.toString(),
      'pickup_token': pickupToken,
      'delivery_token': deliveryToken,
      'created_at': createdAt.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
    };
  }

  Task copyWith({
    String? id,
    String? donorId,
    String? ngoId,
    String? volunteerId,
    Location? pickupLocation,
    Location? dropLocation,
    double? distanceKm,
    String? foodType,
    DateTime? expiryTime,
    bool? requiresCooling,
    TaskStatus? status,
    String? pickupToken,
    String? deliveryToken,
    DateTime? createdAt,
    DateTime? completedAt,
  }) {
    return Task(
      id: id ?? this.id,
      donorId: donorId ?? this.donorId,
      ngoId: ngoId ?? this.ngoId,
      volunteerId: volunteerId ?? this.volunteerId,
      pickupLocation: pickupLocation ?? this.pickupLocation,
      dropLocation: dropLocation ?? this.dropLocation,
      distanceKm: distanceKm ?? this.distanceKm,
      foodType: foodType ?? this.foodType,
      expiryTime: expiryTime ?? this.expiryTime,
      requiresCooling: requiresCooling ?? this.requiresCooling,
      status: status ?? this.status,
      pickupToken: pickupToken ?? this.pickupToken,
      deliveryToken: deliveryToken ?? this.deliveryToken,
      createdAt: createdAt ?? this.createdAt,
      completedAt: completedAt ?? this.completedAt,
    );
  }
}

/// Location Model
class Location {
  final double lat;
  final double lng;

  Location({required this.lat, required this.lng});
}

/// Task Status Enum
enum TaskStatus {
  pending,
  assigned,
  inProgress,
  pickedUp,
  inTransit,
  delivered,
  completed,
  cancelled,
  exception;

  static TaskStatus fromString(String status) {
    switch (status.toUpperCase()) {
      case 'PENDING':
        return TaskStatus.pending;
      case 'ASSIGNED':
        return TaskStatus.assigned;
      case 'IN_PROGRESS':
        return TaskStatus.inProgress;
      case 'PICKED_UP':
        return TaskStatus.pickedUp;
      case 'IN_TRANSIT':
        return TaskStatus.inTransit;
      case 'DELIVERED':
        return TaskStatus.delivered;
      case 'COMPLETED':
        return TaskStatus.completed;
      case 'CANCELLED':
        return TaskStatus.cancelled;
      case 'EXCEPTION':
        return TaskStatus.exception;
      default:
        return TaskStatus.pending;
    }
  }

  @override
  String toString() {
    switch (this) {
      case TaskStatus.pending:
        return 'PENDING';
      case TaskStatus.assigned:
        return 'ASSIGNED';
      case TaskStatus.inProgress:
        return 'IN_PROGRESS';
      case TaskStatus.pickedUp:
        return 'PICKED_UP';
      case TaskStatus.inTransit:
        return 'IN_TRANSIT';
      case TaskStatus.delivered:
        return 'DELIVERED';
      case TaskStatus.completed:
        return 'COMPLETED';
      case TaskStatus.cancelled:
        return 'CANCELLED';
      case TaskStatus.exception:
        return 'EXCEPTION';
    }
  }
}
