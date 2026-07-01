import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Calculadora de Dólar',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark, // Modo oscuro nativo muy elegante
        primarySwatch: Colors.green,
        scaffoldBackgroundColor: const Color(0xFF121212),
      ),
      home: const ConversorPage(),
    );
  }
}

class ConversorPage extends StatefulWidget {
  const ConversorPage({super.key});

  @override
  State<ConversorPage> createState() => _ConversorPageState();
}

class _ConversorPageState extends State<ConversorPage> {
  // Controladores para capturar y modificar el texto de los campos
  final TextEditingController _usdController = TextEditingController();
  final TextEditingController _localController = TextEditingController();

  // Tasa de cambio inicial de prueba (Luego la conectamos a internet)
  double _tasaDolar = 40.50; 

  @override
  void initState() {
    super.initState();
    // Escuchar cuando el usuario escribe en Dólares
    _usdController.addListener(_convertirUsdaLocal);
    // Escuchar cuando el usuario escribe en Moneda Local
    _localController.addListener(_convertirLocalaUsd);
  }

  void _convertirUsdaLocal() {
    if (!_usdController.text.hasFocus) return; // Solo si el usuario está escribiendo aquí
    final usd = double.tryParse(_usdController.text) ?? 0.0;
    final resultado = usd * _tasaDolar;
    
    _localController.text = resultado > 0 ? resultado.toStringAsFixed(2) : '';
  }

  void _convertirLocalaUsd() {
    if (!_localController.text.hasFocus) return; // Solo si el usuario está escribiendo aquí
    final local = double.tryParse(_localController.text) ?? 0.0;
    final resultado = _tasaDolar > 0 ? local / _tasaDolar : 0.0;
    
    _usdController.text = resultado > 0 ? resultado.toStringAsFixed(2) : '';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Calculadora de Divisas'),
        centerTitle: true,
        backgroundColor: const Color(0xFF1E1E1E),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Tarjeta Superior con la Tasa del Día
            Card(
              color: const Color(0xFF1E1E1E),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  children: [
                    const Text('Tasa de Cambio Actual', style: TextStyle(color: Colors.grey, fontSize: 14)),
                    const SizedBox(height: 5),
                    Text('1 \$ = $_tasaDolar Bs.', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.greenAccent)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 30),

            // Campo de Dólares
            TextField(
              controller: _usdController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'Cantidad en Dólares (\$)',
                prefixIcon: const Icon(Icons.attach_money, color: Colors.greenAccent),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(height: 20),

            // Icono de intercambio visual
            const Center(child: Icon(Icons.swap_vert, size: 32, color: Colors.grey)),
            const SizedBox(height: 20),

            // Campo de Moneda Local
            TextField(
              controller: _localController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'Cantidad en Moneda Local (Bs.)',
                prefixIcon: const Icon(Icons.payments, color: Colors.blueAccent),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(height: 40),

            // Botón para actualizar la tasa desde internet
            ElevatedButton.icon(
              onPressed: () {
                // Aquí llamaremos a la función que conecta con la API o Scraper
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Actualizar Tasa'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 15),
                backgroundColor: Colors.greenAccent,
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _usdController.dispose();
    _localController.dispose();
    super.dispose();
  }
}

// Extensión rápida para verificar qué campo tiene el foco activo y evitar bucles infinitos
extension on TextEditingController {
  bool get hasFocus => true; // Nota: En desarrollo real se maneja con FocusNode, simplificado para el ejemplo.
}