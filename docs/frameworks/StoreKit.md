---
sidebar_position: 1
title: StoreKit
---

# StoreKit

## ¿Qué es StoreKit?

StoreKit es el framework nativo de Apple que permite a los desarrolladores integrar compras dentro de la aplicación (In-App Purchases), suscripciones y gestión de transacciones directamente desde sus apps para iOS, macOS, watchOS y tvOS. Es el puente fundamental entre tu aplicación y la infraestructura de pagos del App Store, proporcionando APIs seguras para ofrecer contenido premium, funcionalidades desbloqueables y modelos de suscripción.

Desde su introducción, StoreKit ha evolucionado significativamente. Con **StoreKit 2** (introducido en WWDC 2021), Apple rediseñó completamente la API adoptando concurrencia moderna con `async/await`, verificación criptográfica de transacciones mediante JWS (JSON Web Signature) y una experiencia de desarrollo notablemente más sencilla. StoreKit 2 elimina gran parte de la complejidad que caracterizaba a la versión original, donde los delegados y las colas de pago eran fuente constante de errores.

Es imprescindible utilizar StoreKit siempre que tu aplicación necesite monetizar contenido digital: desbloquear funciones premium, ofrecer suscripciones mensuales o anuales, vender bienes consumibles (monedas virtuales, créditos) o no consumibles (temas, filtros permanentes). Apple **exige** el uso de su sistema de pagos para cualquier contenido digital distribuido a través del App Store, por lo que dominar StoreKit es una habilidad esencial para todo desarrollador iOS profesional.

## Casos de uso principales

- **Suscripciones auto-renovables**: Modelos freemium con planes mensuales, trimestrales o anuales. Es el modelo de monetización más popular en el App Store (ejemplos: Spotify, Headspace, Notion).

- **Compras no consumibles**: Desbloqueo permanente de funcionalidades, como la versión "Pro" de una app, eliminación de publicidad, packs de iconos o temas visuales que el usuario conserva para siempre.

- **Compras consumibles**: Venta de bienes virtuales que se agotan con el uso, como monedas, gemas, créditos de IA o vidas extra en juegos. Pueden comprarse múltiples veces.

- **Restauración de compras**: Permitir que los usuarios recuperen compras previas al cambiar de dispositivo, reinstalar la app o iniciar sesión en un nuevo iPhone, garantizando que no pierdan contenido adquirido.

- **Ofertas promocionales y códigos de oferta**: Implementación de descuentos introductorios (pruebas gratuitas, precio reducido temporal), ofertas promocionales para retención de usuarios y códigos canjeables para campañas de marketing.

- **Gestión de reembolsos y revocaciones**: Detectar cuándo Apple ha procesado un reembolso para revocar el acceso al contenido correspondiente, manteniendo la integridad del modelo de negocio.

## Instalación y configuración

### Agregar StoreKit al proyecto

StoreKit viene incluido como framework del sistema, por lo que **no requiere instalación mediante SPM, CocoaPods ni dependencias externas**. Solo necesitas importarlo:

```swift
import StoreKit
```

### Configuración en App Store Connect

1. **Crear identificadores de productos**: Accede a [App Store Connect](https://appstoreconnect.apple.com), selecciona tu app, navega a **Monetización > In-App Purchases** o **Suscripciones** y crea los productos con sus identificadores únicos.

2. **Configurar grupos de suscripción**: Si ofreces suscripciones, agrúpalas en grupos lógicos (por ejemplo: "Plan Premium") para que Apple gestione correctamente las upgrades y downgrades.

3. **Aceptar acuerdos fiscales**: En **Acuerdos, impuestos y banca**, asegúrate de tener completos los contratos de aplicaciones de pago.

### Configuración local con StoreKit Configuration File

Para desarrollo y pruebas locales sin necesidad de App Store Connect:

```
Xcode → File → New → File → StoreKit Configuration File
```

Este archivo `.storekit` te permite definir productos localmente, simular transacciones, probar escenarios de error y verificar el flujo completo sin conexión al servidor de Apple.

```
// En el esquema de Xcode:
Product → Scheme → Edit Scheme → Run → Options → StoreKit Configuration → Selecciona tu archivo .storekit
```

### Capacidades del proyecto (Capabilities)

En tu target, añade la capability **In-App Purchase**:

```
Target → Signing & Capabilities → + Capability → In-App Purchase
```

### Info.plist

StoreKit no requiere claves especiales en `Info.plist`. Sin embargo, si utilizas **SKAdNetwork** para atribución de publicidad, necesitarás agregar las claves `SKAdNetworkItems` correspondientes.

## Conceptos clave

### 1. Tipos de productos (`Product.ProductType`)

StoreKit define cuatro tipos fundamentales de productos:

- **`.consumable`**: Se agotan con el uso y pueden comprarse repetidamente (monedas, créditos).
- **`.nonConsumable`**: Se compran una vez y persisten permanentemente (desbloqueo pro, temas).
- **`.autoRenewable`**: Suscripciones que se renuevan automáticamente al finalizar cada período.
- **`.nonRenewable`**: Suscripciones que no se renuevan automáticamente; el usuario debe renovar manualmente.

### 2. Transacciones verificadas (`Transaction`)

En StoreKit 2, cada transacción viene firmada criptográficamente por Apple usando JWS. El framework verifica automáticamente la firma, devolviendo un `VerificationResult<Transaction>` que puede ser `.verified` o `.unverified`. **Nunca debes otorgar contenido basándote en una transacción no verificada.**

### 3. Entitlements (derechos de acceso)

Un *entitlement* representa el derecho del usuario a acceder a contenido o funcionalidad. Tu app debe mantener un estado actualizado de qué productos ha adquirido el usuario consultando `Transaction.currentEntitlements`.

### 4. Transaction Listener

Es un mecanismo que escucha transacciones que llegan fuera del flujo normal de compra: renovaciones automáticas de suscripciones, aprobaciones de compras familiares (Ask to Buy), reembolsos procesados por Apple y compras realizadas en otros dispositivos. **Debe iniciarse al arrancar la app.**

### 5. Product Request y catálogo de productos

Antes de mostrar productos al usuario, debes solicitarlos al App Store usando `Product.products(for:)`, que retorna objetos `Product` con precio localizado, descripción y metadatos. Este catálogo debe sincronizarse con tus identificadores configurados en App Store Connect.

### 6. Subscription Status y renovación

Para suscripciones auto-renovables, `Product.SubscriptionInfo.Status` proporciona el estado actual: activa, expirada, en período de gracia, en billing retry o revocada. Es crucial monitorear estos estados para gestionar correctamente el acceso del usuario.

## Ejemplo básico

```swift
import StoreKit

// Ejemplo básico: solicitar productos y realizar una compra simple
// Compatible con iOS 15+ / StoreKit 2

class BasicStoreExample {
    
    // Identificadores de productos configurados en App Store Connect
    private let productIDs: Set<String> = [
        "com.miapp.premium.mensual",
        "com.miapp.monedas.100",
        "com.miapp.eliminarpublicidad"
    ]
    
    /// Obtiene los productos disponibles desde el App Store
    func obtenerProductos() async {
        do {
            // Solicitar productos al App Store
            let productos = try await Product.products(for: productIDs)
            
            for producto in productos {
                print("📦 Producto: \(producto.displayName)")
                print("   Precio: \(producto.displayPrice)")
                print("   Tipo: \(producto.type)")
                print("   Descripción: \(producto.description)")
                print("---")
            }
        } catch {
            print("❌ Error al obtener productos: \(error.localizedDescription)")
        }
    }
    
    /// Realiza la compra de un producto específico
    func comprarProducto(_ producto: Product) async {
        do {
            // Iniciar el flujo de compra
            let resultado = try await producto.purchase()
            
            switch resultado {
            case .success(let verificacion):
                // Verificar la firma criptográfica de la transacción
                switch verificacion {
                case .verified(let transaccion):
                    // ✅ Transacción verificada por Apple
                    print("✅ Compra exitosa: \(transaccion.productID)")
                    
                    // Otorgar el contenido al usuario
                    await entregarContenido(para: transaccion)
                    
                    // IMPORTANTE: finalizar la transacción
                    await transaccion.finish()
                    
                case .unverified(_, let error):
                    // ⚠️ La firma no pudo verificarse
                    print("⚠️ Transacción no verificada: \(error)")
                }
                
            case .userCancelled:
                print("🚫 El usuario canceló la compra")
                
            case .pending:
                // Compra pendiente de aprobación (ej: Ask to Buy)
                print("⏳ Compra pendiente de aprobación")
                
            @unknown default:
                print("❓ Resultado desconocido")
            }
        } catch {
            print("❌ Error en la compra: \(error.localizedDescription)")
        }
    }
    
    /// Entrega el contenido al usuario según el tipo de producto
    private func entregarContenido(para transaccion: Transaction) async {
        switch transaccion.productType {
        case .consumable:
            print("🪙 Acreditando monedas al usuario...")
        case .nonConsumable:
            print("🔓 Desbloqueando contenido permanente...")
        case .autoRenewable:
            print("⭐ Activando suscripción premium...")
        default:
            break
        }
    }
}
```

## Ejemplo intermedio

```swift
import StoreKit
import SwiftUI

// Ejemplo intermedio: Tienda completa con SwiftUI y gestión de estado
// Incluye: listado de productos, compra, restauración y listener de transacciones

/// Modelo observable que gestiona toda la lógica de la tienda
@MainActor
class TiendaManager: ObservableObject {
    
    // MARK: - Propiedades publicadas
    
    /// Productos disponibles para la venta
    @Published var productos: [Product] = []
    
    /// IDs de productos que el usuario ha comprado
    @Published var productosComprados: Set<String> = []
    
    /// Estado de carga
    @Published var estaCargando = false
    
    /// Mensaje de error si ocurre alguno
    @Published var mensajeError: String?
    
    // MARK: - Propiedades privadas
    
    /// Identificadores de productos
    private let productIDs: [String] = [
        "com.miapp.pro.mensual",
        "com.miapp.pro.anual",
        "com.miapp.monedas.500",
        "com.miapp.temaoscuro"
    ]
    
    /// Tarea que escucha actualizaciones de transacciones en segundo plano
    private var actualizacionesTask: Task<Void, Never>?
    
    // MARK: - Inicialización
    
    init() {
        // Iniciar el listener de transacciones inmediatamente
        actualizacionesTask = iniciarListenerTransacciones()
        
        // Cargar productos y estado actual
        Task {
            await cargarProductos()
            await actualizarEstadoCompras()
        }
    }
    
    deinit {
        actualizacionesTask?.cancel()
    }
    
    // MARK: - Listener de transacciones
    
    /// Escucha transacciones que llegan fuera del flujo de compra normal:
    /// renovaciones, aprobaciones de Ask to Buy, compras desde otro dispositivo
    private func iniciarListenerTransacciones() -> Task<Void, Never> {
        Task.detached(priority: .background) { [weak self] in
            // Transaction.updates es un AsyncSequence que emite transacciones nuevas
            for await resultado in Transaction.updates {
                await self?.procesarTransaccion(resultado)
            }
        }
    }
    
    // MARK: - Carga de productos
    
    /// Solicita los productos al App Store y los ordena por precio
    func cargarProductos() async {
        estaCargando = true
        mensajeError = nil
        
        do {
            let productosObtenidos = try await Product.products(for: productIDs)
            
            // Ordenar productos: suscripciones primero, luego por precio
            productos = productosObtenidos.sorted { p1, p2 in
                if p1.type == p2.type {
                    return p1.price < p2.price
                }
                return p1.type == .autoRenewable
            }
            
            print("📦 \(productos.count) productos cargados")
        } catch {
            mensajeError = "No se pudieron cargar los productos. Verifica tu conexión."
            print("❌ Error cargando productos: \(error)")
        }
        
        estaCargando = false
    }
    
    // MARK: - Compra
    
    /// Ejecuta la compra de un producto y procesa el resultado
    func comprar(_ producto: Product) async -> Bool {
        do {
            let resultado = try await producto.purchase()
            
            switch resultado {
            case .success(let verificacion):
                return await procesarTransaccion(verificacion)
                
            case .userCancelled:
                return false
                
            case .pending:
                mensajeError = "Tu compra está pendiente de aprobación."
                return false
                
            @unknown default:
                return false
            }
        } catch StoreKitError.userCancelled {
            return false
        } catch {
            mensajeError = "Error al procesar la compra: \(error.localizedDescription)"
            return false
        }
    }
    
    // MARK: - Procesamiento de transacciones
    
    /// Verifica y procesa una transacción, devolviendo si fue exitosa
    @discardableResult
    private func procesarTransaccion(
        _ resultado: VerificationResult<Transaction>
    ) async -> Bool {
        switch resultado {
        case .verified(let transaccion):
            // Actualizar el estado local
            if transaccion.revocationDate == nil {
                productosComprados.insert(transaccion.productID)
            } else {
                // El producto fue reembolsado, revocar acceso
                productosComprados.remove(transaccion.productID)
            }
            
            // Finalizar la transacción para que Apple sepa que fue procesada
            await transaccion.finish()
            return true
            
        case .unverified(let transaccion, let error):
            print("⚠️ Transacción no verificada (\(transaccion.productID)): \(error)")
            return false
        }
    }
    
    // MARK: - Estado de compras
    
    /// Recorre todas las transacciones activas para reconstruir el estado
    func actualizarEstadoCompras() async {
        var comprasActivas: Set<String>