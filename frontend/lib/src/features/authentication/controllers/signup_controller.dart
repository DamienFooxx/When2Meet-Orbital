import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SignUpController extends GetxController {
  static SignUpController get instance => Get.find();

  //TextField Controllers to get data from TextFields
  final email = TextEditingController();
  final password = TextEditingController();
  final fullName = TextEditingController();
  final phoneNo = TextEditingController();

  //Call these Functions from Design & they will do the logic
  void registerUser(String email, String password) {

  }

  //Get phoneNo from user and pass it to Auth Repository for Firebase Authentication
  void phoneAuthentication(String phoneNo) {

  }
}
