# Arquitectura del Proyecto: CryptoVault Cross-Platform

Este documento describe la estructura técnica y las decisiones de diseño tomadas para garantizar la seguridad, escalabilidad y compatibilidad entre plataformas (Python y Android).

## 1. Principios de Diseño
El proyecto sigue los principios de **Clean Architecture** y el patrón **MVVM** (Model-View-ViewModel).

### Capas del Sistema:
1. **Dominio / Core (Nivel más alto):** Contiene las reglas de negocio puras. Aquí reside la lógica de cifrado AES-256-GCM. No depende de ninguna librería externa de UI o Base de Datos.
2. **Datos (Data):** Gestiona la persistencia. Es la capa encargada de hablar con la API de Google Drive y el almacenamiento local. Implementa el "Pessimistic Locking" para evitar colisiones de escritura.
3. **Presentación (UI):** Implementada mediante MVVM. La lógica de la interfaz está desacoplada de los elementos visuales, permitiendo que la App de Android y la de Escritorio compartan comportamientos lógicos idénticos.

## 2. Seguridad (Zero-Knowledge)
El sistema está diseñado bajo el modelo de "Conocimiento Cero":
- **Derivación de Clave:** Se utiliza PBKDF2 con 600,000 iteraciones y SHA-256.
- **Cifrado Simétrico:** AES-256 en modo GCM para garantizar confidencialidad e integridad de los datos.
- **Sincronización:** Los datos se almacenan en el `appDataFolder` de Google Drive, invisible para el usuario y otras aplicaciones.

## 3. Compatibilidad Multiplataforma
Para asegurar que un archivo cifrado en Python pueda ser abierto en Android, se ha definido un "Contrato de Datos" estricto:
- **Formato:** JSON serializado.
- **Estructura del Paquete:** `[Salt(16b)] + [IV(12b)] + [Ciphertext(var)] + [Tag(16b)]`.
- **Codificación:** Base64 para el transporte de datos binarios.


cryptovault-crossplatform/
├── .gitignore               # Configuración para evitar subir basura o secretos
├── README.md                # Presentación general del proyecto
├── docs/                    # Documentación técnica profunda
│   └── architecture.md      # El documento que generamos abajo
│
├── desktop_python/          # App de Escritorio (Python)
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── requirements.txt     # Dependencias (cryptography, google-api, etc.)
│   ├── src/                 # Código fuente (Clean Architecture)
│   │   ├── core/            # Entidades y Lógica de Negocio (Cifrado)
│   │   ├── data/            # Implementación de Drive y Local Storage
│   │   ├── ui/              # Interfaz (MVVM: Vistas y ViewModels)
│   │   └── utils/           # Helpers de sistema
│   └── tests/               # Pruebas unitarias
│
└── mobile_android/          # App Móvil (Kotlin + Compose)
    ├── app/
    │   └── src/
    │       ├── main/
    │       │   ├── java/com/tuusuario/cryptovault/
    │       │   │   ├── domain/   # Lógica pura (equivalente a core en Python)
    │       │   │   ├── data/     # Repositorios y API de Drive
    │       │   │   └── ui/       # Pantallas en Jetpack Compose (MVVM)
    │       │   └── res/          # Recursos visuales
    │       └── test/             # Pruebas unitarias
    └── build.gradle         # Configuración de dependencias Android

---
*Este documento es parte del portafolio técnico de bzorzet98.*
