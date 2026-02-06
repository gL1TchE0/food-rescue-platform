import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';

class DonorInputScreen extends StatefulWidget {
  const DonorInputScreen({super.key});

  @override
  State<DonorInputScreen> createState() => _DonorInputScreenState();
}

class _DonorInputScreenState extends State<DonorInputScreen> {
  final _formKey = GlobalKey<FormState>();
  
  final TextEditingController _donorNameController = TextEditingController();
  final TextEditingController _addressController = TextEditingController();
  final TextEditingController _quantityController = TextEditingController();
  
  String foodType = 'VEG';
  double? quantityKg;
  double? latitude;
  double? longitude;
  bool _isLoadingLocation = false;

  final List<String> _foodTypes = ['VEG', 'NON_VEG', 'VEGAN', 'MIXED'];

  Future<void> _getCurrentLocation() async {
    setState(() {
      _isLoadingLocation = true;
    });

    try {
      bool serviceEnabled;
      LocationPermission permission;

      serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw 'Location services are disabled.';
      }

      permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw 'Location permissions are denied';
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        throw 'Location permissions are permanently denied, we cannot request permissions.';
      } 

      Position position = await Geolocator.getCurrentPosition();
      setState(() {
        latitude = position.latitude;
        longitude = position.longitude;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error getting location: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingLocation = false;
        });
      }
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (latitude == null || longitude == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture location before submitting.')),
      );
      return;
    }

    quantityKg = double.parse(_quantityController.text);

    // Generate expires_at: current time + 4 hours (ISO 8601 without milliseconds for example compliance)
    final now = DateTime.now();
    final expiryTime = now.add(const Duration(hours: 4));
    final expiresAt = "${expiryTime.toIso8601String().split('.').first}";

    final Map<String, dynamic> donationData = {
      'donor_name': _donorNameController.text,
      'food_type': foodType,
      'quantity_kg': quantityKg,
      'latitude': latitude,
      'longitude': longitude,
      'address': _addressController.text,
      'expires_at': expiresAt,
    };

    try {
      final response = await http.post(
        Uri.parse('http://10.219.207.52:8000/api/donations'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(donationData),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Food donation submitted successfully! Expires at: $expiresAt')),
          );
          _clearForm();
          Navigator.pop(context); // Navigate back to home screen
        }
      } else {
        throw 'Submission failed with status: ${response.statusCode}';
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Submission failed. Try again.')),
        );
      }
    }
  }

  void _clearForm() {
    _donorNameController.clear();
    _addressController.clear();
    _quantityController.clear();
    setState(() {
      foodType = 'VEG';
      quantityKg = null;
      latitude = null;
      longitude = null;
    });
  }

  @override
  void dispose() {
    _donorNameController.dispose();
    _addressController.dispose();
    _quantityController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Donate Food'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _donorNameController,
                decoration: const InputDecoration(
                  labelText: 'Restaurant / Donor Name',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter donor name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _addressController,
                decoration: const InputDecoration(
                  labelText: 'Pickup Address',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter address';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: foodType,
                decoration: const InputDecoration(
                  labelText: 'Food Type',
                  border: OutlineInputBorder(),
                ),
                items: _foodTypes.map((String type) {
                  return DropdownMenuItem<String>(
                    value: type,
                    child: Text(type),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    foodType = newValue!;
                  });
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _quantityController,
                decoration: const InputDecoration(
                  labelText: 'Quantity (kg)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter quantity';
                  }
                  if (double.tryParse(value) == null) {
                    return 'Please enter a valid number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Lat: ${latitude?.toStringAsFixed(6) ?? "Not set"}'),
                        Text('Long: ${longitude?.toStringAsFixed(6) ?? "Not set"}'),
                      ],
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: _isLoadingLocation ? null : _getCurrentLocation,
                    icon: _isLoadingLocation 
                      ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.location_on),
                    label: const Text('Use Current Location'),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _submitForm,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Submit Donation', style: TextStyle(fontSize: 18)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
