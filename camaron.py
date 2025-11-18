def calcular_alimentacion_inteligente(temp_agua, biomasa_kg, precio_saco=25.00):
    """
    Calcula la ración óptima de alimento y el ahorro financiero
    basado en la temperatura del agua (SST).
    
    Args:
        temp_agua (float): Temperatura actual en °C.
        biomasa_kg (float): Kilos totales de camarón en la piscina.
        precio_saco (float): Costo promedio del saco de 25kg (USD).
    """
    
    # 1. Definir la Tasa de Alimentación (La lógica biológica)
    if temp_agua > 26:
        tasa = 0.03  # 3% (Metabolismo activo/óptimo)
        estado = "🟢 Óptimo"
    elif 24 <= temp_agua <= 26:
        tasa = 0.02  # 2% (Metabolismo medio)
        estado = "🟡 Precaución"
    else:
        tasa = 0.005 # 0.5% (Metabolismo lento/Frío)
        estado = "🔴 Crítico (Frío)"

    # 2. Cálculos de Ingeniería
    alimento_necesario_kg = biomasa_kg * tasa
    sacos_necesarios = alimento_necesario_kg / 25
    costo_dia = sacos_necesarios * precio_saco
    
    # 3. Comparativa (¿Cuánto gastaría si no usara datos?)
    # Asumimos que un camaronero "ciego" siempre alimenta al 3%
    gasto_ciego = (biomasa_kg * 0.03 / 25) * precio_saco 
    ahorro = gasto_ciego - costo_dia

    # 4. Reporte
    print(f"--- REPORTE DE ALIMENTACIÓN ({estado}) ---")
    print(f"🌡️  Temperatura del Agua: {temp_agua}°C")
    print(f"⚖️  Biomasa en piscina: {biomasa_kg} kg")
    print(f"---------------------------------------")
    print(f"📦 Alimento Sugerido: {alimento_necesario_kg:.1f} kg ({sacos_necesarios:.1f} sacos)")
    print(f"💵 Costo Hoy: ${costo_dia:.2f}")
    
    if ahorro > 0:
        print(f"✅ AHORRO GENERADO HOY: ${ahorro:.2f} (vs. Alimentación Estándar)")
        print("💡 Consejo: El agua está fría. No desperdicies alimento.")
    else:
        print("⚡ Producción al máximo. ¡A alimentar!")

# --- SIMULACIÓN (Lo que pasaría hoy en el Golfo) ---
# Supongamos una piscina mediana con 5,000 kg de camarón
# Y supongamos que hoy el agua amaneció fría a 23°C
calcular_alimentacion_inteligente(temp_agua=23.0, biomasa_kg=5000)