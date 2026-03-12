---
sidebar_position: 1
title: Seguridad
---

# Seguridad en Aplicaciones iOS

## Introducción

La seguridad en el desarrollo iOS no es un feature opcional: es una **responsabilidad fundamental**. Cada línea de código que escribimos puede ser la diferencia entre proteger o exponer los datos sensibles de millones de usuarios. En Latinoamérica, donde el sector fintech crece exponencialmente y las aplicaciones de banca móvil, billeteras digitales y servicios gubernamentales se multiplican, dominar los principios de seguridad no solo te hace mejor desarrollador — te convierte en un profesional indispensable.

Este tema abarca desde el almacenamiento seguro de datos hasta la comunicación cifrada con servidores, pasando por la protección contra ingeniería inversa, jailbreak detection y las mejores prácticas que Apple recomienda.

---

## ¿Por qué es crítico para un dev iOS en LATAM?

1. **Regulaciones crecientes**: Países como México (Ley Fintech), Brasil (LGPD), Colombia (Ley 1581) y Argentina (Ley 25.326) exigen protección de datos personales. Un fallo de seguridad puede significar sanciones millonarias.
2. **Boom fintech**: Mercado Pago, Nubank, Rappi, Ualá — las apps financieras de la región manejan datos bancarios reales. La seguridad es requisito no negociable.
3. **Confianza del usuario**: En mercados donde la adopción digital todavía está en crecimiento, una brecha de seguridad puede destruir la confianza que costó años construir.
4. **Diferencial profesional**: Pocos developers dominan seguridad a fondo. Especializarte te posiciona para roles senior y de arquitectura.

---

## Pilares de la Seguridad en iOS

### 1. Almacenamiento Seguro con Keychain

**Nunca** almacenes contraseñas, tokens o datos sensibles en `UserDefaults`, archivos planos o Core Data sin cifrado. El **Keychain** es el mecanismo correcto.

```swift
import Security

struct KeychainHelper {

    enum KeychainError: Error {
        case duplicateItem
        case itemNotFound
        case unexpectedStatus(OSStatus)
    }

    // MARK: - Guardar datos en Keychain

    static func save(
        service: String,
        account: String,
        data: Data
    ) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecDuplicateItem {
            // Si ya existe, actualizamos
            let updateQuery: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrService as String: service,
                kSecAttrAccount as String: account
            ]
            let updateAttributes: [String: Any] = [
                kSecValueData as String: data
            ]
            let updateStatus = SecItemUpdate(
                updateQuery as CFDictionary,
                updateAttributes as CFDictionary
            )
            guard updateStatus == errSecSuccess else {
                throw KeychainError.unexpectedStatus(updateStatus)
            }
        } else if status != errSecSuccess {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    // MARK: - Leer datos del Keychain

    static func read(
        service: String,
        account: String
    ) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess, let data = result as? Data else {
            if status == errSecItemNotFound {
                throw KeychainError.itemNotFound
            }
            throw KeychainError.unexpectedStatus(status)
        }

        return data
    }

    // MARK: - Eliminar datos del Keychain

    static func delete(
        service: String,
        account: String
    ) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }
}
```

**Uso práctico:**

```swift
// Guardar un token de autenticación
let token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
let tokenData = Data(token.utf8)

try KeychainHelper.save(
    service: "com.miapp.auth",
    account: "accessToken",
    data: tokenData
)

// Recuperar el token
let savedData = try KeychainHelper.read(
    service: "com.miapp.auth",
    account: "accessToken"
)
let savedToken = String(data: savedData, encoding: .utf8)
print("Token recuperado: \(savedToken ?? "nil")")
```

> ⚠️ **Nota importante**: Usa `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` para que los datos solo sean accesibles cuando el dispositivo está desbloqueado y no se transfieran a otros dispositivos ni a backups.

---

### 2. Autenticación Biométrica con LocalAuthentication

Integrar Face ID o Touch ID agrega una capa de seguridad que los usuarios de LATAM valoran enormemente, especialmente en apps financieras.

```swift
import LocalAuthentication

final class BiometricAuthManager {

    enum BiometricError: Error, LocalizedError {
        case notAvailable
        case authenticationFailed
        case userCancelled
        case systemError(Error)

        var errorDescription: String? {
            switch self {
            case .notAvailable:
                return "La autenticación biométrica no está disponible en este dispositivo."
            case .authenticationFailed:
                return "No se pudo verificar tu identidad."
            case .userCancelled:
                return "Autenticación cancelada por el usuario."
            case .systemError(let error):
                return "Error del sistema: \(error.localizedDescription)"
            }
        }
    }

    /// Verifica si el dispositivo soporta biometría
    static func canUseBiometrics() -> Bool {
        let context = LAContext()
        var error: NSError?
        return context.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            error: &error
        )
    }

    /// Tipo de biometría disponible
    static func biometryType() -> LABiometryType {
        let context = LAContext()
        var error: NSError?
        context.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            error: &error
        )
        return context.biometryType
    }

    /// Autenticación biométrica con async/await
    static func authenticate(
        reason: String = "Verifica tu identidad para continuar"
    ) async throws -> Bool {
        let context = LAContext()
        context.localizedCancelTitle = "Cancelar"
        context.localizedFallbackTitle = "Usar contraseña"

        var error: NSError?
        guard context.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            error: &error
        ) else {
            throw BiometricError.notAvailable
        }

        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            return success
        } catch let authError as LAError {
            switch authError.code {
            case .userCancel, .appCancel:
                throw BiometricError.userCancelled
            case .authenticationFailed:
                throw BiometricError.authenticationFailed
            default:
                throw BiometricError.systemError(authError)
            }
        }
    }
}
```

**Uso en un ViewModel:**

```swift
@MainActor
final class LoginViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var errorMessage: String?

    func authenticateWithBiometrics() async {
        do {
            let success = try await BiometricAuthManager.authenticate(
                reason: "Inicia sesión con Face ID"
            )
            if success {
                isAuthenticated = true
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```

> 📱 **Recuerda**: Agrega la clave `NSFaceIDUsageDescription` en tu `Info.plist` con una descripción clara en español para tus usuarios.

---

### 3. Certificate Pinning para Comunicaciones Seguras

HTTPS no es suficiente. Un atacante en una red WiFi pública (muy común en cafeterías y espacios de coworking en LATAM) puede realizar ataques Man-in-the-Middle con certificados falsos. **Certificate Pinning** garantiza que tu app solo se comunique con tu servidor legítimo.

```swift
import Foundation
import CryptoKit

final class PinnedURLSessionDelegate: NSObject, URLSessionDelegate {

    /// Hash SHA-256 del certificado público de tu servidor
    /// Puedes obtenerlo ejecutando:
    /// openssl s_client -connect tudominio.com:443 | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64
    private let pinnedHashes: Set<String> = [
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=", // Hash principal
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC="  // Hash de respaldo
    ]

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard challenge.protectionSpace.authenticationMethod
                == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust
        else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Evaluar la cadena de certificados
        let policies = [SecPolicyCreateSSL(true, challenge.protectionSpace.host as CFString)]
        SecTrustSetPolicies(serverTrust, policies as CFTypeRef)

        var error: CFError?
        guard SecTrustEvaluateWithError(serverTrust, &error) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Verificar el pin del certificado
        let certificateCount = SecTrustGetCertificateCount(serverTrust)

        for index in 0..<certificateCount {
            guard let certificate = SecTrustCopyCertificateChain(serverTrust)
                    .map({ ($0 as! [SecCertificate]) })?[safe: index],
                  let publicKey = SecCertificateCopyKey(certificate),
                  let publicKeyData = SecKeyCopyExternalRepresentation(publicKey, nil)
            else {
                continue
            }

            let keyData = publicKeyData as Data
            let hash = SHA256.hash(data: keyData)
            let hashString = Data(hash).base64EncodedString()

            if pinnedHashes.contains(hashString) {
                let credential = URLCredential(trust: serverTrust)
                completionHandler(.useCredential, credential)
                return
            }
        }

        // Ningún certificado coincidió: rechazar la conexión
        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}

// Extensión auxiliar para acceso seguro a arrays
private extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
```

**Configuración del `URLSession`:**

```swift
final class SecureNetworkClient {
    private let session: URLSession

    init() {
        let delegate = PinnedURLSessionDelegate()
        let configuration = URLSessionConfiguration.ephemeral
        configuration.urlCache = nil // No cachear respuestas sensibles
        configuration.httpCookieStorage = nil
        self.session = URLSession(
            configuration: configuration,
            delegate: delegate,
            delegateQueue: nil
        )
    }

    func request(url: URL) async throws -> Data {
        let (data, response) = try await session.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }
        return data
    }
}
```

---

### 4. Detección de Jailbreak

En LATAM, la distribución de apps por fuera de la App Store y el uso de dispositivos con jailbreak es más común de lo que pensamos. Para apps financieras o gubernamentales, detectar estas modificaciones es esencial.

```swift
import Foundation
import UIKit

struct JailbreakDetector {

    /// Verifica múltiples indicadores de jailbreak
    static func isDeviceJailbroken() -> Bool {
        #if targetEnvironment(simulator)
        return false // No verificar en el simulador
        #else
        return checkSuspiciousPaths()
            || checkSuspiciousApps()
            || checkWritePermissions()
            || checkDynamicLibraries()
            || checkForkCapability()
        #endif
    }

    // MARK: - Verificaciones individuales

    /// Archivos y directorios típicos de jailbreak
    private static func checkSuspiciousPaths() -> Bool {
        let suspiciousPaths = [
            "/Applications/Cydia.app",
            "/Applications/Sileo.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/usr/bin/ssh",
            "/private/var/lib/apt/",
            "/private/var/lib/cydia",
            "/private/var/stash",
            "/var/cache/apt/",
            "/var/lib/dpkg/",
            "/usr/libexec/cydia/"
        ]

        return suspiciousPaths.contains { path in
            FileManager.default.fileExists(atPath: path)
        }
    }

    /// Apps de jailbreak que pueden abrirse vía URL scheme
    private static func checkSuspiciousApps() -> Bool {
        let suspiciousSchemes = [
            "cydia://",
            "sileo://",
            "zbra://",
            "filza://"
        ]

        return suspiciousSchemes.contains { scheme in
            guard let url = URL(string: scheme) else { return false }
            return UIApplication.shared.canOpenURL(url)
        }
    }

    /// En un dispositivo normal, no puedes escribir fuera del sandbox
    private