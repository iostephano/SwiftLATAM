---
sidebar_position: 1
title: Demo Fintech App
---

# Demo Fintech App: Construyendo una Aplicación Financiera Completa en iOS

## Introducción

Latinoamérica es uno de los mercados fintech de mayor crecimiento en el mundo. Con más de **2,000 startups fintech** operando en la región y países como México, Brasil, Colombia y Argentina liderando la adopción, dominar el desarrollo de aplicaciones financieras en iOS no es solo una habilidad técnica: es una oportunidad profesional concreta.

En esta demo construiremos **WalletLATAM**, una aplicación fintech funcional que incluye autenticación biométrica, visualización de saldo, transferencias entre usuarios y un historial de transacciones. Cada decisión arquitectónica está pensada para cumplir con los estándares de seguridad y experiencia de usuario que el sector financiero exige.

---

## ¿Por qué es importante para un dev iOS en LATAM?

- **Demanda laboral real**: empresas como Nubank, Mercado Pago, Ualá, Clip, Konfío y Rappi buscan constantemente desarrolladores iOS con experiencia en apps financieras.
- **Regulaciones locales**: entender cómo manejar datos sensibles (CNBV en México, BCRA en Argentina, SFC en Colombia) te diferencia de otros candidatos.
- **Inclusión financiera**: millones de personas en la región acceden a servicios financieros por primera vez a través del móvil. Tu código tiene impacto social directo.
- **Salarios competitivos**: el nicho fintech ofrece compensaciones superiores al promedio del mercado iOS en la región.

---

## Arquitectura del Proyecto

Utilizaremos **MVVM + Coordinators** con inyección de dependencias, un patrón ampliamente adoptado por equipos fintech por su testabilidad y separación clara de responsabilidades.

```
WalletLATAM/
├── App/
│   ├── AppDelegate.swift
│   ├── SceneDelegate.swift
│   └── AppCoordinator.swift
├── Core/
│   ├── Network/
│   │   ├── APIClient.swift
│   │   ├── Endpoint.swift
│   │   └── NetworkError.swift
│   ├── Security/
│   │   ├── BiometricAuthManager.swift
│   │   ├── KeychainManager.swift
│   │   └── CertificatePinning.swift
│   └── Extensions/
├── Features/
│   ├── Authentication/
│   ├── Dashboard/
│   ├── Transfers/
│   └── TransactionHistory/
├── Design/
│   ├── Components/
│   ├── Tokens/
│   └── Theme.swift
└── Resources/
```

---

## Paso 1: Seguridad Primero — Autenticación Biométrica

En una app fintech, la seguridad no es negociable. Implementemos autenticación con Face ID / Touch ID usando `LocalAuthentication`:

```swift
import LocalAuthentication

final class BiometricAuthManager {

    enum BiometricError: Error {
        case notAvailable
        case authenticationFailed
        case userCancelled
        case unknown(Error)
    }

    private let context = LAContext()

    var biometricType: LABiometryType {
        var error: NSError?
        context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
        return context.biometryType
    }

    var isBiometricAvailable: Bool {
        var error: NSError?
        return context.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            error: &error
        )
    }

    func authenticate() async -> Result<Bool, BiometricError> {
        guard isBiometricAvailable else {
            return .failure(.notAvailable)
        }

        let reason = "Inicia sesión en tu cuenta WalletLATAM"

        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            return .success(success)
        } catch let error as LAError {
            switch error.code {
            case .userCancel:
                return .failure(.userCancelled)
            case .authenticationFailed:
                return .failure(.authenticationFailed)
            default:
                return .failure(.unknown(error))
            }
        } catch {
            return .failure(.unknown(error))
        }
    }
}
```

> **Nota regulatoria**: En México, la CNBV exige autenticación de dos factores para operaciones financieras. La biometría puede ser uno de esos factores, pero nunca el único.

---

## Paso 2: Almacenamiento Seguro con Keychain

Nunca almacenes tokens, PINs ni datos sensibles en `UserDefaults`. Usemos Keychain:

```swift
import Security
import Foundation

final class KeychainManager {

    enum KeychainError: Error {
        case duplicateItem
        case itemNotFound
        case unexpectedStatus(OSStatus)
        case invalidData
    }

    static let shared = KeychainManager()
    private init() {}

    func save(_ data: Data, forKey key: String, accessibility: CFString = kSecAttrAccessibleWhenUnlockedThisDeviceOnly) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: accessibility
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecDuplicateItem {
            let updateQuery: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrAccount as String: key
            ]
            let attributes: [String: Any] = [
                kSecValueData as String: data
            ]
            let updateStatus = SecItemUpdate(
                updateQuery as CFDictionary,
                attributes as CFDictionary
            )
            guard updateStatus == errSecSuccess else {
                throw KeychainError.unexpectedStatus(updateStatus)
            }
        } else if status != errSecSuccess {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    func retrieve(forKey key: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess else {
            if status == errSecItemNotFound {
                throw KeychainError.itemNotFound
            }
            throw KeychainError.unexpectedStatus(status)
        }

        guard let data = result as? Data else {
            throw KeychainError.invalidData
        }

        return data
    }

    func delete(forKey key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    // MARK: - Convenience Methods

    func saveToken(_ token: String, forKey key: String) throws {
        guard let data = token.data(using: .utf8) else {
            throw KeychainError.invalidData
        }
        try save(data, forKey: key)
    }

    func retrieveToken(forKey key: String) throws -> String {
        let data = try retrieve(forKey: key)
        guard let token = String(data: data, encoding: .utf8) else {
            throw KeychainError.invalidData
        }
        return token
    }
}
```

---

## Paso 3: Capa de Red con Certificate Pinning

Las apps fintech **deben** implementar certificate pinning para prevenir ataques man-in-the-middle:

```swift
import Foundation

final class APIClient: NSObject {

    static let shared = APIClient()

    private lazy var session: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60
        configuration.waitsForConnectivity = true
        return URLSession(
            configuration: configuration,
            delegate: self,
            delegateQueue: nil
        )
    }()

    // Hash SHA256 del certificado de tu servidor
    private let pinnedCertificateHash = "TU_HASH_SHA256_AQUI"

    func request<T: Decodable>(
        endpoint: Endpoint,
        responseType: T.Type
    ) async throws -> T {
        var urlRequest = try endpoint.asURLRequest()

        // Agregar token de autenticación
        if let token = try? KeychainManager.shared.retrieveToken(forKey: "auth_token") {
            urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let (data, response) = try await session.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            return try decoder.decode(T.self, from: data)
        case 401:
            throw NetworkError.unauthorized
        case 429:
            throw NetworkError.rateLimited
        default:
            throw NetworkError.serverError(statusCode: httpResponse.statusCode)
        }
    }
}

// MARK: - Certificate Pinning
extension APIClient: URLSessionDelegate {

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust,
              let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        let serverCertificateData = SecCertificateCopyData(certificate) as Data
        let serverHash = serverCertificateData.sha256Hash

        if serverHash == pinnedCertificateHash {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}

// MARK: - Endpoint Definition
struct Endpoint {
    let path: String
    let method: HTTPMethod
    let body: Encodable?
    let queryItems: [URLQueryItem]?

    private static let baseURL = "https://api.walletlatam.com/v1"

    func asURLRequest() throws -> URLRequest {
        var components = URLComponents(string: Self.baseURL + path)!
        components.queryItems = queryItems

        var request = URLRequest(url: components.url!)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let body = body {
            let encoder = JSONEncoder()
            encoder.keyEncodingStrategy = .convertToSnakeCase
            request.httpBody = try encoder.encode(body)
        }

        return request
    }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}

enum NetworkError: Error, LocalizedError {
    case invalidResponse
    case unauthorized
    case rateLimited
    case serverError(statusCode: Int)
    case noConnection

    var errorDescription: String? {
        switch self {
        case .invalidResponse: return "Respuesta inválida del servidor"
        case .unauthorized: return "Sesión expirada. Inicia sesión nuevamente"
        case .rateLimited: return "Demasiados intentos. Espera un momento"
        case .serverError(let code): return "Error del servidor (\(code))"
        case .noConnection: return "Sin conexión a internet"
        }
    }
}
```

---

## Paso 4: Modelos del Dominio Financiero

```swift
import Foundation

// MARK: - User Account
struct Account: Codable, Identifiable {
    let id: String
    let accountNumber: String
    let clabe: String // CLABE interbancaria (México)
    let currency: Currency
    let balance: Decimal
    let availableBalance: Decimal
    let accountType: AccountType
    let isActive: Bool

    var formattedBalance: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = currency.rawValue
        formatter.locale = currency.locale
        formatter.minimumFractionDigits = 2
        formatter.maximumFractionDigits = 2
        return formatter.string(from: balance as NSDecimalNumber) ?? "$0.00"
    }
}

enum Currency: String, Codable {
    case mxn = "MXN"
    case cop = "COP"
    case ars = "ARS"
    case usd = "USD"
    case brl = "BRL"
    case clp = "CLP"
    case pen = "PEN"

    var locale: Locale {
        switch self {
        case .mxn: return Locale(identifier: "es_MX")
        case .cop: return Locale(identifier: "es_CO")
        case .ars: return Locale(identifier: "es_AR")
        case .usd: return Locale(identifier: "en_US")
        case .brl: return Locale(identifier: "pt_BR")
        case .clp: return Locale(identifier: "es_CL")
        case .pen: return Locale(identifier: "es_PE")
        }
    }

    var symbol: String {
        switch self {
        case .mxn, .cop, .ars, .usd, .clp: return "$"
        case .brl: return "R$"
        case .pen: return "S/"
        }
    }
}

enum AccountType: String, Codable {
    case checking = "checking"
    case savings = "savings"
    case digital = "digital"

    var displayName: String {
        switch self {
        case .checking: return "Cuenta Corriente"
        case .savings: return "Cuenta de Ahorro"
        case .digital: return "Cuenta Digital"
        }
    }
}

// MARK: - Transaction
struct Transaction: Codable, Identifiable {
    let id: String
    let type: TransactionType
    let amount: Decimal
    let currency: Currency
    let description: String
    let category: TransactionCategory
    let date: Date
    let status: TransactionStatus
    let counterpartyName: String?
    let reference: String?

    var isIncome: Bool {
        type == .deposit || type == .transferIn
    }

    var formattedAmount: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = currency.rawValue
        formatter.locale = currency.locale
        let prefix = isIncome ? "+" : "-"
        let formatted = formatter.string(from: amount as NSDecimalNumber) ?? "$0.00"
        return "\(prefix)\(formatted)"
    }

    var formattedDate: String {
        let formatter = DateFormatter()
        