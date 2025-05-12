import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = 'http://192.168.1.1:8000/api';

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
      print('✅ Login successful! Token: $token');
      return true;
    } else {
      print('❌ Login failed: ${response.statusCode}');
      print(response.body);
      return false;
    }
  }

  Future<bool> register(String username, String email, String password1, String password2) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/registration/'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'username': username,
        'email': email,
        'password1': password1,
        'password2': password2,
      }),
    );

    if (response.statusCode == 201) {
      print('✅ Registered!');
      return true;
    } else {
      print('❌ Registration failed: ${response.statusCode}');
      print('Response: ${response.body}');
      return false;
    }
  }


// Add more endpoints here: register, getEvents, createEvent, etc.
}
