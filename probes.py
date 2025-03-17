import os
import time
import subprocess
import json  # Módulo para procesar JSON

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

def get_pod_status():
    """Obtiene el estado actual del pod (ej: Running, Pending, CrashLoopBackOff)."""
    cmd = f'kubectl get pod {POD_NAME} --no-headers -o custom-columns=":status.phase"'
    return run_command(cmd) or "Unknown"

def get_pod_readiness_status():
    """Verifica si el pod está en estado 'Ready' usando kubectl get pods."""
    cmd = f'kubectl get pod {POD_NAME} --no-headers -o custom-columns=":status.containerStatuses[0].ready"'
    output = run_command(cmd)
    return output == "true"

def get_pod_restarts():
    """Obtiene el número de reinicios del pod."""
    cmd = f'kubectl get pod {POD_NAME} --no-headers -o custom-columns=":status.containerStatuses[0].restartCount"'
    output = run_command(cmd)
    return int(output) if output and output.isdigit() else 0

### 🔥 **Simulación de Fallos** ###
def simulate_liveness_failure():
    """Simula un fallo del Liveness Probe matando completamente Nginx."""
    print("\n🚨 **Simulando fallo de Liveness:** Matando completamente Nginx (el pod debería reiniciarse) 🚫")
    run_command(f'kubectl exec -it {POD_NAME} -- sh -c "nginx -s stop || pkill -9 nginx || killall -9 nginx"')

    print("\n🔍 **Esperando a que Kubernetes reinicie el pod...**")
    time.sleep(10)

    if get_pod_restarts() > 0:
        print("✅ **El pod ha sido reiniciado correctamente por el Liveness Probe!** 🎯")
    else:
        print("❌ **El pod NO se reinició. Verifica la configuración del Liveness Probe.**")

def simulate_readiness_failure():
    """Simula una falla de Readiness pausando Nginx."""
    print("\n🚨 **Simulando fallo de Readiness:** Pausando Nginx (el pod debería marcarse como 'Not Ready' 🟡 sin reiniciarse) 🔥")
    run_command(f'kubectl exec -it {POD_NAME} -- sh -c "pkill -STOP nginx"')

    print("\n🔍 **Esperando a que Kubernetes detecte el fallo...**")
    
    for i in range(5):
        time.sleep(3)
        if not get_pod_readiness_status():
            print(f"✅ **El pod ha sido marcado como 'Not Ready' después de {3*(i+1)}s!** 🎯")
            return
        print(f"⌛ Esperando... {3*(i+1)}s")

    print("❌ **El pod NO ha sido marcado como 'Not Ready'.** Verifica la configuración del probe de Readiness.")

def restore_readiness():
    """Restaura Readiness Probe reanudando Nginx."""
    print("\n🔄 **Restaurando Readiness:** Reanudando Nginx ✅")
    run_command(f'kubectl exec -it {POD_NAME} -- sh -c "pkill -CONT nginx"')

    print("\n🔍 **Esperando a que el pod vuelva a estar 'Ready'...**")
    
    for i in range(5):
        time.sleep(3)
        if get_pod_readiness_status():
            print(f"✅ **El pod ha sido marcado como 'Ready' después de {3*(i+1)}s!** 🎯")
            return
        print(f"⌛ Esperando... {3*(i+1)}s")

    print("❌ **El pod sigue 'Not Ready'.** Revisa la configuración de Readiness Probe.")

def simulate_startup_failure():
    """Simula una falla de Startup Probe deteniendo Nginx en el arranque."""
    print("\n🚨 **Simulando fallo de Startup:** Matando Nginx antes de que inicie correctamente 🔥")
    run_command(f'kubectl exec -it {POD_NAME} -- sh -c "nginx -s stop || pkill -9 nginx || killall -9 nginx"')

    print("\n🔍 **Esperando que Kubernetes detecte la falla del Startup Probe...**")
    
    for i in range(6):
        time.sleep(5)  # Espera en intervalos de 5 segundos
        restarts = get_pod_restarts()
        if restarts > 0:
            print(f"✅ **El pod ha sido reiniciado por el Startup Probe después de {5*(i+1)}s!** 🎯")
            return
        print(f"⌛ Esperando... {5*(i+1)}s (Reinicios detectados: {restarts})")

    print("❌ **El pod NO se reinició. Verifica la configuración del probe de Startup.**")

### 🎯 **Menú Principal** ###
def main():
    print("\n🔍 **Estado inicial del pod:**")
    print(f"📌 Estado: {get_pod_status()} (Readiness: {get_pod_readiness_status()})")

    print("\n🛠 **¿Qué prueba quieres realizar?**")
    print("1️⃣ **Fallo Liveness:** Matar completamente Nginx (debería reiniciar el pod 🚨)")
    print("2️⃣ **Fallo Readiness:** Pausar Nginx (debería marcar el pod como 'Not Ready' 🟡 sin reiniciarlo)")
    print("3️⃣ **Restaurar Readiness:** Reanudar Nginx (debería marcar el pod como 'Ready' ✅)")
    print("4️⃣ **Fallo Startup:** Simular fallo en el arranque de Nginx (debería reiniciar el pod) 🔥")
    print("5️⃣ **Salir**")

    choice = input("👉 Ingresa el número de la opción: ")

    if choice == "1":
        simulate_liveness_failure()  # 🔥 Liveness Probe (matar Nginx completamente)
    elif choice == "2":
        simulate_readiness_failure()  # 🔥 Readiness Probe (pausar Nginx)
    elif choice == "3":
        restore_readiness()  # 🔄 Restaurar Readiness
    elif choice == "4":
        simulate_startup_failure()  # 🔥 Simular fallo de Startup
    else:
        print("👋 Saliendo del script.")

if __name__ == "__main__":
    main()
