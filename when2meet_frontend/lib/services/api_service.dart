import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = 'http://127.0.0.1:8000/';

  String? token;

  Future<bool> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      body: {
        'email': email,
        'password': password,
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      token = data['key'];
      print('✅ Token received: $token');
      return true;
    } else {
      print('❌ Login error: ${response.body}');
      return false;
    }
  }

  Future<bool> register(String email, String password1, String password2) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/registration/'),
      body: {
        'email': email,
        'password1': password1,
        'password2': password2,
      },
    );

    return response.statusCode == 201 || response.statusCode == 200;
  }

// Add more endpoints here: register, getEvents, createEvent, etc.
}
