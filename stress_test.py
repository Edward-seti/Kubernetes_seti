import subprocess
import time

# 🔍 Nombre del pod (ajústalo según tu caso)
POD_NAME = "mi-app-546bc45b5b-vwclb"

def run_command(cmd):
    """Ejecuta un comando en la shell y maneja errores."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el comando: {cmd}")
        print(f"🔍 Detalles del error: {e.stderr}")
        return None

def install_stress_ng():
    """Instala stress-ng dentro del contenedor en nginx:alpine."""
    print("\n🛠 Instalando stress-ng en el pod...")
    result = run_command(f'kubectl exec -it {POD_NAME} -- sh -c "apk add --no-cache stress-ng"')
    
    if result is not None:
        print("✅ stress-ng instalado correctamente.")
    else:
        print("❌ Error al instalar stress-ng. Verifica el pod.")

def run_stress_ng():
    """Ejecuta stress-ng para cargar la memoria."""
    print("\n🔥 Ejecutando stress-ng para cargar memoria...")
    run_command(f'kubectl exec -it {POD_NAME} -- sh -c "stress-ng --vm 2 --vm-bytes 256M --timeout 600s"')
    print("✅ Prueba de carga iniciada. Monitoreando el consumo de memoria...")

def monitor_memory():
    """Monitorea el uso de memoria del pod en Kubernetes."""
    print("\n📊 Monitoreando consumo de memoria del pod:")
    for _ in range(10):  # Monitorear durante 10 iteraciones (~1 minuto)
        mem_usage = run_command(f'kubectl top pod {POD_NAME} --no-headers')
        print(f"📊 Uso de memoria del pod: {mem_usage}")
        time.sleep(5)  # Espera 5 segundos entre mediciones

# 🚀 **Ejecutar el proceso**
install_stress_ng()
run_stress_ng()
monitor_memory()
