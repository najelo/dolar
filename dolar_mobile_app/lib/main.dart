import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Inicializa Supabase con tus credenciales
  await Supabase.initialize(
    url: 'https://oxsimejylqyjahlagvzy.supabase.co',
    anonKey: 'sb_publishable_O_oQDHdJWqxXaL3UzZHkzw_-F6O6-sA',
  );
runApp(const DolarMonitorApp());
}

class DolarMonitorApp extends StatelessWidget {
  const DolarMonitorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0F0F12),
        colorScheme: const ColorScheme.dark(primary: Colors.amber),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  HomeScreenState createState() => HomeScreenState();
}

class HomeScreenState extends State<HomeScreen> {
  final supabase = Supabase.instance.client;
  double _tasaSeleccionada = 0.0;
  String _nombreSeleccionado = "";
  final TextEditingController _usdController = TextEditingController();
  final TextEditingController _vesController = TextEditingController();

  Future<double> _fetchTasa(String banco) async {
    try {
      final data = await supabase.from('tasas_monitoreo').select().eq('id', 1).single();
      switch (banco) {
        case "BCV": return (data['bcv'] as num).toDouble();
        case "BINANCE": return (data['binance'] as num).toDouble();
        case "Binance - Banesco": return (data['binance_banesco'] as num).toDouble();
        case "Binance - Mercantil": return (data['binance_mercantil'] as num).toDouble();
        case "Binance - BDV": return (data['binance_bdv'] as num).toDouble();
        case "Binance - PagoMóvil": return (data['binance_pagomovil'] as num).toDouble();
        default: return 0.0;
      }
    } catch (e) { return 0.0; }
  }

  void _actualizarSeleccion(String nombre, double valor) {
    setState(() {
      _nombreSeleccionado = nombre;
      _tasaSeleccionada = valor;
      _usdController.clear();
      _vesController.clear();
    });
  }

  void _calcular(String value, bool esUsd) {
    if (_tasaSeleccionada == 0) return;
    double monto = double.tryParse(value) ?? 0.0;
    setState(() {
      if (esUsd) {
        _vesController.text = (monto * _tasaSeleccionada).toStringAsFixed(2);
      } else {
        _usdController.text = (monto / _tasaSeleccionada).toStringAsFixed(2);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF1E1E26), Color(0xFF0F0F12)],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildBotonModerno("BCV", _nombreSeleccionado == "BCV", Colors.blueAccent, Colors.white, () async {
                    double tasa = await _fetchTasa("BCV");
                    _actualizarSeleccion("BCV", tasa);
                  }),
                  const SizedBox(width: 15),
                  PopupMenuButton<String>(
                    onSelected: (val) async {
                      double tasa = await _fetchTasa(val);
                      _actualizarSeleccion(val, tasa);
                    },
                    itemBuilder: (context) => [
                      const PopupMenuItem(value: "BINANCE", child: Text("Binance Promedio")),
                      const PopupMenuItem(value: "Binance - Banesco", child: Text("Banesco")),
                      const PopupMenuItem(value: "Binance - Mercantil", child: Text("Mercantil")),
                      const PopupMenuItem(value: "Binance - BDV", child: Text("BDV")),
                      const PopupMenuItem(value: "Binance - PagoMóvil", child: Text("PagoMóvil")),
                    ],
                    child: _buildBotonModerno("BINANCE ▼", _nombreSeleccionado.contains("Binance"), Colors.amber, Colors.black, null),
                  ),
                ],
              ),
              const SizedBox(height: 40),
              Text("$_nombreSeleccionado: $_tasaSeleccionada Bs", style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 20),
              _buildInput(_usdController, "Dólares", "\$", true),
              _buildInput(_vesController, "Bolívares", "Bs", false),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBotonModerno(String text, bool active, Color color, Color textColor, VoidCallback? onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.symmetric(horizontal: 25, vertical: 15),
        decoration: BoxDecoration(
          color: active ? color : Colors.white.withOpacity(0.05),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: active ? color : Colors.white24),
          boxShadow: active ? [BoxShadow(color: color.withOpacity(0.3), blurRadius: 10, offset: const Offset(0, 4))] : [],
        ),
        child: Text(text, style: TextStyle(color: active ? textColor : Colors.white, fontWeight: FontWeight.bold)),
      ),
    );
  }

  Widget _buildInput(TextEditingController controller, String label, String prefix, bool esUsd) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(color: Colors.white.withOpacity(0.05), borderRadius: BorderRadius.circular(20)),
      child: TextField(
        controller: controller,
        onChanged: (v) => _calcular(v, esUsd),
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label, prefixText: "$prefix ", border: InputBorder.none),
      ),
    );
  }
}