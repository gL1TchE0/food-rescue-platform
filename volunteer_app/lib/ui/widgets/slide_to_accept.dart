import 'package:flutter/material.dart';
import 'dart:async';

/// Slide to Accept Widget
/// Used for "Slide to Online" and task acceptance
/// Spring physics animation (250ms ease-out)

class SlideToAccept extends StatefulWidget {
  final String text;
  final Color backgroundColor;
  final Color foregroundColor;
  final IconData icon;
  final VoidCallback onConfirm;
  final bool isLoading;

  const SlideToAccept({
    super.key,
    required this.text,
    required this.backgroundColor,
    required this.foregroundColor,
    required this.icon,
    required this.onConfirm,
    this.isLoading = false,
  });

  @override
  State<SlideToAccept> createState() => _SlideToAcceptState();
}

class _SlideToAcceptState extends State<SlideToAccept>
    with SingleTickerProviderStateMixin {
  double _dragPosition = 0;
  bool _isDragging = false;
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    );
    _animation = Tween<double>(begin: 0, end: 0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _onHorizontalDragUpdate(DragUpdateDetails details, double maxWidth) {
    setState(() {
      _dragPosition = (_dragPosition + details.delta.dx)
          .clamp(0.0, maxWidth - 70);
    });
  }

  void _onHorizontalDragEnd(DragEndDetails details, double maxWidth) {
    setState(() => _isDragging = false);

    // Check if dragged past threshold (80%)
    if (_dragPosition > (maxWidth - 70) * 0.8) {
      // Success - trigger action
      setState(() => _dragPosition = maxWidth - 70);
      Future.delayed(const Duration(milliseconds: 200), () {
        widget.onConfirm();
        _resetPosition();
      });
    } else {
      // Reset position with animation
      _resetPosition();
    }
  }

  void _resetPosition() {
    _animation = Tween<double>(begin: _dragPosition, end: 0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );
    _animationController.forward(from: 0).then((_) {
      setState(() => _dragPosition = 0);
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        if (_animationController.isAnimating && !_isDragging) {
          _dragPosition = _animation.value;
        }

        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 20),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final maxWidth = constraints.maxWidth;

              return Container(
                height: 70,
                decoration: BoxDecoration(
                  color: widget.backgroundColor,
                  borderRadius: BorderRadius.circular(35),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Stack(
                  children: [
                    // Background Text
                    Center(
                      child: Text(
                        widget.text,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: widget.foregroundColor.withOpacity(0.5),
                        ),
                      ),
                    ),

                    // Sliding Button
                    AnimatedPositioned(
                      duration: _isDragging
                          ? Duration.zero
                          : const Duration(milliseconds: 250),
                      curve: Curves.easeOut,
                      left: _dragPosition,
                      child: GestureDetector(
                        onHorizontalDragStart: (_) {
                          setState(() => _isDragging = true);
                        },
                        onHorizontalDragUpdate: (details) {
                          _onHorizontalDragUpdate(details, maxWidth);
                        },
                        onHorizontalDragEnd: (details) {
                          _onHorizontalDragEnd(details, maxWidth);
                        },
                        child: Container(
                          width: 70,
                          height: 70,
                          decoration: BoxDecoration(
                            color: widget.foregroundColor,
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: widget.foregroundColor.withOpacity(0.3),
                                blurRadius: 15,
                                offset: const Offset(0, 5),
                              ),
                            ],
                          ),
                          child: widget.isLoading
                              ? const Padding(
                                  padding: EdgeInsets.all(20.0),
                                  child: CircularProgressIndicator(
                                    strokeWidth: 3,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white),
                                  ),
                                )
                              : Icon(
                                  widget.icon,
                                  color: Colors.white,
                                  size: 32,
                                ),
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }
}
