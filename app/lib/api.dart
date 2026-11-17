import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final String message;
  final int status;
  ApiException(this.message, this.status);
  @override
  String toString() => message;
}

/// Thin client for the EnduraForge server (API v1).
class Api {
  final String baseUrl;
  final String? token;
  Api(String url, {this.token}) : baseUrl = url.trim().replaceAll(RegExp(r'/+$'), '');

  Map<String, String> get _headers => <String, String>{
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Future<dynamic> _send(String method, String path, {Object? body}) async {
    final uri = Uri.parse('$baseUrl$path');
    http.Response r;
    try {
      final b = body == null ? null : jsonEncode(body);
      switch (method) {
        case 'GET':
          r = await http.get(uri, headers: _headers).timeout(const Duration(seconds: 20));
          break;
        case 'POST':
          r = await http.post(uri, headers: _headers, body: b).timeout(const Duration(seconds: 20));
          break;
        default:
          r = await http.put(uri, headers: _headers, body: b).timeout(const Duration(seconds: 20));
      }
    } catch (e) {
      throw ApiException('Cannot reach the server at $baseUrl. Check the address and your internet.', 0);
    }
    if (r.statusCode >= 200 && r.statusCode < 300) {
      if (r.body.isEmpty) return null;
      final type = r.headers['content-type'] ?? '';
      return type.contains('json') ? jsonDecode(utf8.decode(r.bodyBytes)) : utf8.decode(r.bodyBytes);
    }
    var msg = 'Server error ${r.statusCode}';
    try {
      final j = jsonDecode(utf8.decode(r.bodyBytes));
      if (j is Map && j['detail'] != null) msg = j['detail'].toString();
    } catch (_) {}
    throw ApiException(msg, r.statusCode);
  }

  Future<Map<String, dynamic>> health() async => Map<String, dynamic>.from(await _send('GET', '/health') as Map);

  Future<Map<String, dynamic>> login(String email, String password, {bool register = false}) async {
    final res = await _send('POST', register ? '/api/v1/auth/register' : '/api/v1/auth/login', body: {'email': email, 'password': password});
    return Map<String, dynamic>.from(res as Map);
  }

  Future<void> putDay(String iso, Map<String, dynamic> data, String updatedAt) async {
    await _send('PUT', '/api/v1/days/$iso', body: {'data': data, 'updated_at': updatedAt});
  }

  Future<void> putResult(String key, double? value, String updatedAt) async {
    await _send('PUT', '/api/v1/results/${Uri.encodeComponent(key)}', body: {'value': value, 'updated_at': updatedAt});
  }

  Future<Map<String, dynamic>> sync(String? since) async {
    final q = since == null ? '' : '?since=${Uri.encodeQueryComponent(since)}';
    return Map<String, dynamic>.from(await _send('GET', '/api/v1/sync$q') as Map);
  }

  Future<String> exportCsv() async => (await _send('GET', '/api/v1/export/days.csv')).toString();

  /// The plan built for this account, as raw JSON text (cached on the phone as-is).
  Future<String> plan() async {
    try {
      final r = await http.get(Uri.parse('$baseUrl/api/v1/plan'), headers: _headers).timeout(const Duration(seconds: 60));
      if (r.statusCode == 200) return utf8.decode(r.bodyBytes);
      throw ApiException('Could not download the plan (${r.statusCode})', r.statusCode);
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException('Cannot reach the server at $baseUrl.', 0);
    }
  }

  Future<void> putConfig(Map<String, dynamic> config, String updatedAt) async {
    await _send('PUT', '/api/v1/config', body: {'config': config, 'updated_at': updatedAt});
  }

  Future<void> putActivities(List<Map<String, dynamic>> acts) async {
    await _send('PUT', '/api/v1/activities', body: acts);
  }

  Future<Map<String, dynamic>> importGarmin(String csv) async =>
      Map<String, dynamic>.from(await _send('POST', '/api/v1/activities/import', body: {'csv': csv, 'apply_baseline': true}) as Map);
}
