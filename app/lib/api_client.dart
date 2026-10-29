import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  /// Errors that will never succeed if retried (bad data) — the change is dropped.
  bool get permanent => statusCode >= 400 && statusCode < 500 && statusCode != 401 && statusCode != 408 && statusCode != 429;

  @override
  String toString() => statusCode == 401 ? 'Token rejected by the server' : 'Server error $statusCode: $message';
}

/// Thin HTTP wrapper for the Race Plan API. Network failures surface as normal exceptions
/// (SocketException, TimeoutException, http.ClientException) and mean "offline".
class ApiClient {
  final String baseUrl;
  final String token;
  final http.Client _http;
  static const _timeout = Duration(seconds: 20);

  ApiClient(String baseUrl, this.token, {http.Client? client})
      : baseUrl = baseUrl.trim().replaceAll(RegExp(r'/+$'), ''),
        _http = client ?? http.Client();

  Map<String, String> get _headers => {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  dynamic _decode(http.Response r) {
    if (r.statusCode < 200 || r.statusCode >= 300) {
      String msg = r.body;
      try {
        final j = jsonDecode(r.body);
        if (j is Map && j['detail'] != null) msg = j['detail'].toString();
      } catch (_) {}
      throw ApiException(r.statusCode, msg);
    }
    if (r.body.isEmpty) return null;
    return jsonDecode(utf8.decode(r.bodyBytes));
  }

  Future<dynamic> get(String path) async => _decode(await _http.get(_uri(path), headers: _headers).timeout(_timeout));

  Future<dynamic> put(String path, Map<String, dynamic>? body) async =>
      _decode(await _http.put(_uri(path), headers: _headers, body: jsonEncode(body ?? {})).timeout(_timeout));

  Future<dynamic> delete(String path) async => _decode(await _http.delete(_uri(path), headers: _headers).timeout(_timeout));

  /// Health check (no token) followed by an authenticated call, so the settings screen can tell
  /// "server unreachable" apart from "wrong token".
  Future<String> testConnection() async {
    try {
      await _decode(await _http.get(_uri('/api/health')).timeout(_timeout));
    } on ApiException catch (e) {
      return 'Server answered with error ${e.statusCode}. Check the URL.';
    } catch (e) {
      return 'Cannot reach the server. Check the URL and that the API is running.';
    }
    try {
      await get('/api/dashboard');
      return 'ok';
    } on ApiException catch (e) {
      return e.statusCode == 401 ? 'Server reached, but the token is wrong.' : e.toString();
    } catch (e) {
      return 'Server reached, but the request failed: $e';
    }
  }
}
