---
sidebar_position: 1
title: PassKit
---

# PassKit

## ¿Qué es PassKit?

PassKit es el framework de Apple que permite a los desarrolladores crear, distribuir y gestionar **pases digitales** dentro del ecosistema de Apple Wallet (anteriormente conocido como Passbook). Estos pases pueden representar tarjetas de embarque, entradas a eventos, cupones de descuento, tarjetas de fidelización, tarjetas de regalo y cualquier otro tipo de credencial o documento digital que un usuario pueda necesitar llevar consigo. PassKit actúa como puente entre tu aplicación y la app Wallet del dispositivo, proporcionando una experiencia nativa y fluida para el usuario final.

Además de la gestión de pases, PassKit incluye las APIs necesarias para integrar **Apple Pay** en tus aplicaciones, permitiendo a los usuarios realizar pagos de forma segura mediante sus tarjetas de crédito, débito o prepago almacenadas en Wallet. Esto abarca desde pagos dentro de la app (in-app purchases de productos físicos y servicios) hasta pagos en la web a través de Safari y pagos en comercios físicos mediante NFC.

Este framework es fundamental cuando necesitas ofrecer experiencias de pago sin fricción, distribuir pases digitales actualizables en tiempo real o integrar programas de fidelización directamente en el dispositivo del usuario. Su uso es especialmente relevante en aplicaciones de comercio electrónico, transporte, hostelería, entretenimiento y servicios financieros, donde la conveniencia y la seguridad del usuario son prioritarias.

## Casos de uso principales

- **Pagos con Apple Pay**: Implementar pagos seguros dentro de tu app para productos físicos, servicios o suscripciones. Los usuarios autentican la transacción con Face ID, Touch ID o su código de acceso, eliminando la necesidad de introducir datos de tarjeta manualmente.

- **Tarjetas de embarque digitales**: Aerolíneas y empresas de transporte pueden emitir tarjetas de embarque que se actualizan automáticamente con cambios de puerta, retrasos o información relevante del vuelo directamente en Apple Wallet.

- **Entradas para eventos**: Distribución de entradas para conciertos, conferencias, eventos deportivos o cualquier espectáculo, con código de barras o QR escaneable directamente desde Wallet, incluyendo notificaciones basadas en ubicación.

- **Tarjetas de fidelización**: Programas de puntos y recompensas que se actualizan automáticamente cada vez que el usuario realiza una compra, mostrando el saldo de puntos actualizado sin necesidad de abrir la app principal.

- **Cupones y ofertas promocionales**: Distribución de descuentos y promociones que aparecen automáticamente en la pantalla de bloqueo del usuario cuando se encuentra cerca de la tienda, gracias a las notificaciones basadas en geolocalización.

- **Tarjetas de acceso y credenciales**: Llaves digitales para hoteles, oficinas o gimnasios que permiten el acceso mediante la aproximación del dispositivo a un lector NFC compatible, sustituyendo las tarjetas físicas tradicionales.

## Instalación y configuración

### Agregar el framework al proyecto

PassKit viene incluido en el SDK de iOS, por lo que no necesitas instalar dependencias externas. Solo debes importarlo en los archivos donde lo utilices:

```swift
import PassKit
```

### Configuración de Apple Pay

Para utilizar Apple Pay, necesitas realizar varios pasos de configuración:

**1. Activar la capability en Xcode:**

Abre tu proyecto en Xcode, selecciona tu target, ve a la pestaña **"Signing & Capabilities"** y añade **"Apple Pay"**. Selecciona los Merchant IDs que utilizarás.

**2. Crear un Merchant ID en el portal de desarrollador:**

Accede a [Apple Developer Portal](https://developer.apple.com/account), navega a **Certificates, Identifiers & Profiles** → **Identifiers** → **Merchant IDs** y crea un nuevo identificador con el formato `merchant.com.tuempresa.tuapp`.

**3. Configurar el certificado de procesamiento de pagos:**

Genera un **Payment Processing Certificate** asociado a tu Merchant ID. Este certificado lo necesitará tu proveedor de pagos (Stripe, Adyen, Braintree, etc.) para descifrar los tokens de pago.

### Configuración para pases personalizados

Para crear y distribuir tus propios pases de Wallet, necesitas:

**1. Crear un Pass Type ID:**

En el portal de desarrollador, navega a **Identifiers** → **Pass Type IDs** y crea uno con formato `pass.com.tuempresa.tuapp.tipopase`.

**2. Generar un certificado de firma:**

Asocia un certificado de firma al Pass Type ID. Este certificado se utiliza para firmar digitalmente los pases `.pkpass` que generes desde tu servidor.

### Entitlements necesarios

El archivo de entitlements se actualiza automáticamente al añadir las capabilities en Xcode. Verifica que contenga:

```xml
<key>com.apple.developer.in-app-payments</key>
<array>
    <string>merchant.com.tuempresa.tuapp</string>
</array>
```

### Permisos en Info.plist

Para funcionalidades que involucren NFC o ubicación (notificaciones de pases basadas en geolocalización), puede ser necesario añadir:

```xml
<key>NFCReaderUsageDescription</key>
<string>Necesitamos acceso a NFC para procesar pagos sin contacto.</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Necesitamos tu ubicación para mostrarte pases relevantes cercanos.</string>
```

## Conceptos clave

### 1. PKPass y PKPassLibrary

`PKPass` representa un pase individual almacenado en Apple Wallet. Contiene toda la información visual y de datos del pase (número de serie, tipo, campos de texto, códigos de barras, etc.). `PKPassLibrary` es la clase que te permite interactuar con la biblioteca de pases del usuario: consultar pases existentes, añadir nuevos, eliminarlos y verificar si Wallet está disponible en el dispositivo.

### 2. PKPaymentRequest

Es el objeto central para configurar una transacción de Apple Pay. Define el comerciante (`merchantIdentifier`), las redes de pago aceptadas (Visa, Mastercard, Amex), el país, la moneda, los artículos a cobrar (`PKPaymentSummaryItem`) y las capacidades del comerciante. Una configuración correcta de este objeto es crucial para que la hoja de pago se presente correctamente.

### 3. PKPaymentAuthorizationController / ViewController

Son los controladores que presentan la interfaz nativa de Apple Pay al usuario. `PKPaymentAuthorizationViewController` es la versión UIKit y `PKPaymentAuthorizationController` es la versión independiente de UI que funciona tanto en UIKit como en contextos donde no hay una jerarquía de vistas (por ejemplo, extensiones). Ambos reciben un `PKPaymentRequest` y notifican el resultado a través de sus delegates.

### 4. PKPaymentToken

Cuando el usuario autoriza un pago con Apple Pay, recibes un `PKPaymentToken` que contiene los datos de pago cifrados. Este token nunca contiene el número real de la tarjeta; en su lugar, utiliza un **Device Account Number** tokenizado. Debes enviar este token a tu servidor backend, que a su vez lo reenvía a tu procesador de pagos para completar la transacción.

### 5. PKAddPassesViewController

Controlador de vista que presenta una interfaz estándar de Apple para que el usuario previsualice y añada un pase a su Wallet. Es la forma recomendada de ofrecer la adición de pases, ya que proporciona una experiencia consistente con el resto del sistema operativo.

### 6. PKPaymentButton y PKAddPassButton

Botones estándar proporcionados por Apple con diseños predefinidos que cumplen con las directrices de la interfaz humana (HIG). `PKPaymentButton` muestra botones como "Comprar con Apple Pay" o "Pagar con Apple Pay", mientras que `PKAddPassButton` muestra el botón "Añadir a Apple Wallet". Usar estos botones es obligatorio para pasar la revisión de la App Store.

## Ejemplo básico

Este ejemplo muestra cómo verificar la disponibilidad de Apple Pay y presentar un botón de pago:

```swift
import UIKit
import PassKit

class SimplePaymentViewController: UIViewController {

    // MARK: - Ciclo de vida

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        configurarBotonApplePay()
    }

    // MARK: - Configuración del botón

    private func configurarBotonApplePay() {
        // Verificar si el dispositivo soporta Apple Pay
        // y si el usuario tiene tarjetas configuradas
        guard PKPaymentAuthorizationViewController.canMakePayments(),
              PKPaymentAuthorizationViewController.canMakePayments(
                usingNetworks: redesSoportadas
              ) else {
            mostrarMensajeNoDisponible()
            return
        }

        // Crear el botón estándar de Apple Pay
        let botonPago = PKPaymentButton(
            paymentButtonType: .buy,
            paymentButtonStyle: .automatic
        )
        botonPago.addTarget(
            self,
            action: #selector(iniciarPago),
            for: .touchUpInside
        )
        botonPago.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(botonPago)
        NSLayoutConstraint.activate([
            botonPago.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            botonPago.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            botonPago.widthAnchor.constraint(equalToConstant: 280),
            botonPago.heightAnchor.constraint(equalToConstant: 50)
        ])
    }

    // Redes de pago que acepta tu comercio
    private var redesSoportadas: [PKPaymentNetwork] {
        [.visa, .masterCard, .amex, .discover]
    }

    // MARK: - Iniciar pago

    @objc private func iniciarPago() {
        // Crear la solicitud de pago
        let solicitud = PKPaymentRequest()
        solicitud.merchantIdentifier = "merchant.com.tuempresa.tuapp"
        solicitud.supportedNetworks = redesSoportadas
        solicitud.merchantCapabilities = .threeDSecure
        solicitud.countryCode = "ES"
        solicitud.currencyCode = "EUR"

        // Definir los artículos del pago
        solicitud.paymentSummaryItems = [
            PKPaymentSummaryItem(label: "Camiseta Premium", amount: 29.99),
            PKPaymentSummaryItem(label: "Envío estándar", amount: 4.99),
            PKPaymentSummaryItem(label: "Mi Tienda S.L.", amount: 34.98)
        ]

        // Presentar la hoja de pago de Apple Pay
        guard let controladorPago = PKPaymentAuthorizationViewController(
            paymentRequest: solicitud
        ) else {
            print("Error: No se pudo crear el controlador de pago")
            return
        }

        controladorPago.delegate = self
        present(controladorPago, animated: true)
    }

    private func mostrarMensajeNoDisponible() {
        let etiqueta = UILabel()
        etiqueta.text = "Apple Pay no está disponible en este dispositivo"
        etiqueta.textAlignment = .center
        etiqueta.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(etiqueta)
        NSLayoutConstraint.activate([
            etiqueta.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            etiqueta.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
}

// MARK: - PKPaymentAuthorizationViewControllerDelegate

extension SimplePaymentViewController: PKPaymentAuthorizationViewControllerDelegate {

    func paymentAuthorizationViewController(
        _ controller: PKPaymentAuthorizationViewController,
        didAuthorizePayment payment: PKPayment,
        handler completion: @escaping (PKPaymentAuthorizationResult) -> Void
    ) {
        // Aquí enviarías payment.token a tu servidor para procesar el pago
        print("Token recibido: \(payment.token)")

        // Simular procesamiento exitoso
        completion(PKPaymentAuthorizationResult(status: .success, errors: nil))
    }

    func paymentAuthorizationViewControllerDidFinish(
        _ controller: PKPaymentAuthorizationViewController
    ) {
        // Cerrar la hoja de pago cuando el usuario termina o cancela
        controller.dismiss(animated: true)
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra cómo crear un servicio de pago reutilizable y añadir pases a Apple Wallet:

```swift
import PassKit
import UIKit

// MARK: - Modelo de producto

struct Producto {
    let nombre: String
    let precio: NSDecimalNumber
    let cantidad: Int

    /// Calcula el subtotal del producto
    var subtotal: NSDecimalNumber {
        precio.multiplying(by: NSDecimalNumber(value: cantidad))
    }
}

// MARK: - Modelo de pedido

struct Pedido {
    let productos: [Producto]
    let costoEnvio: NSDecimalNumber
    let nombreComercio: String

    /// Calcula el total del pedido
    var total: NSDecimalNumber {
        let subtotalProductos = productos.reduce(NSDecimalNumber.zero) { parcial, producto in
            parcial.adding(producto.subtotal)
        }
        return subtotalProductos.adding(costoEnvio)
    }

    /// Genera los items de resumen para Apple Pay
    func generarItemsResumen() -> [PKPaymentSummaryItem] {
        var items: [PKPaymentSummaryItem] = productos.map { producto in
            PKPaymentSummaryItem(
                label: "\(producto.nombre) x\(producto.cantidad)",
                amount: producto.subtotal
            )
        }

        // Añadir envío si tiene costo
        if costoEnvio.compare(NSDecimalNumber.zero) == .orderedDescending {
            items.append(
                PKPaymentSummaryItem(label: "Envío", amount: costoEnvio)
            )
        }

        // El último item SIEMPRE debe ser el total con el nombre del comercio
        items.append(
            PKPaymentSummaryItem(label: nombreComercio, amount: total)
        )

        return items
    }
}

// MARK: - Resultado del pago

enum ResultadoPago {
    case exitoso(tokenData: Data)
    case fallido(Error)
    case cancelado
}

// MARK: - Servicio de Apple Pay

protocol ServicioApplePayDelegate: AnyObject {
    func servicioPago(_ servicio: ServicioApplePay, finalizoConResultado resultado: ResultadoPago)
}

class ServicioApplePay: NSObject {

    // MARK: - Propiedades

    weak var delegate: ServicioApplePayDelegate?

    private let merchantIdentifier: String
    private let countryCode: String
    private let currencyCode: String

    private let redesSoportadas: [PKPaymentNetwork] = [
        .visa, .masterCard, .amex, .discover, .maestro
    ]

    // MARK: - Inicialización

    init(
        merchantIdentifier: String,
        countryCode: String = "ES",
        currencyCode: String = "