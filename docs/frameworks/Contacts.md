---
sidebar_position: 1
title: Contacts
---

# Contacts

## ¿Qué es Contacts?

**Contacts** es el framework nativo de Apple que proporciona acceso programático a la base de datos de contactos del dispositivo del usuario. Permite leer, crear, actualizar y eliminar contactos y grupos de contactos de forma segura y eficiente, respetando siempre la privacidad del usuario mediante un sistema de permisos explícitos.

Este framework reemplazó al antiguo `AddressBook` (basado en C) a partir de iOS 9, ofreciendo una API moderna, orientada a objetos y completamente compatible con Swift. Contacts trabaja con objetos inmutables (`CNContact`) y sus contrapartes mutables (`CNMutableContact`), siguiendo un patrón de diseño que garantiza la seguridad en entornos concurrentes y la consistencia de los datos.

Utilizar Contacts es esencial cuando tu aplicación necesita interactuar con la agenda del usuario: desde mostrar una lista de contactos para compartir contenido, hasta sincronizar información con un servidor remoto, autocompletar campos de formulario o crear funcionalidades sociales dentro de la app. Apple proporciona además el framework complementario `ContactsUI`, que ofrece controladores de interfaz de usuario listos para usar.

## Casos de uso principales

- **Selección de contactos para compartir:** Permitir al usuario elegir uno o varios contactos de su agenda para enviar invitaciones, compartir contenido o asignar participantes a eventos.

- **Autocompletado de formularios:** Rellenar automáticamente campos como nombre, teléfono, email y dirección a partir de los datos de contacto existentes, mejorando la experiencia de usuario.

- **Sincronización con servidor remoto:** Leer contactos del dispositivo para subirlos a un backend (con consentimiento del usuario) y mantener una lista de amigos o conexiones actualizada.

- **Creación y edición de contactos:** Permitir que la app cree nuevos contactos o actualice los existentes directamente desde la interfaz de la aplicación, por ejemplo al guardar datos de un nuevo cliente o proveedor.

- **Búsqueda y filtrado avanzado:** Implementar funcionalidades de búsqueda inteligente sobre la agenda, filtrando por nombre, empresa, ciudad u otros criterios personalizados.

- **Detección de contactos duplicados:** Analizar la base de datos de contactos para identificar y gestionar entradas duplicadas, ayudando al usuario a mantener su agenda organizada.

## Instalación y configuración

### Importación del framework

Contacts es un framework del sistema incluido en el SDK de iOS, macOS, watchOS y Catalyst. No requiere instalación mediante gestores de paquetes. Simplemente importa el módulo en el archivo donde lo necesites:

```swift
import Contacts
import ContactsUI // Opcional: solo si necesitas los controladores de UI prediseñados
```

### Permisos en Info.plist

El acceso a los contactos es una operación sensible a la privacidad. **Es obligatorio** declarar el motivo de uso en el archivo `Info.plist`:

```xml
<key>NSContactsUsageDescription</key>
<string>Necesitamos acceder a tus contactos para que puedas invitar amigos a la aplicación.</string>
```

> ⚠️ **Si no incluyes esta clave, la app se cerrará inmediatamente al intentar acceder a los contactos.** El mensaje que proporciones se mostrará al usuario en el diálogo de permisos del sistema.

### Solicitud de permisos en tiempo de ejecución

```swift
import Contacts

func solicitarPermisoContactos() {
    let store = CNContactStore()

    store.requestAccess(for: .contacts) { concedido, error in
        if concedido {
            print("✅ Permiso concedido para acceder a contactos")
        } else if let error = error {
            print("❌ Permiso denegado: \(error.localizedDescription)")
        }
    }
}
```

### Nota sobre iOS 18 y acceso limitado

A partir de **iOS 18**, Apple introdujo el concepto de **acceso limitado a contactos**. El usuario puede conceder acceso solo a contactos específicos en lugar de a toda la agenda. Es fundamental que tu app maneje correctamente este escenario verificando el nivel de autorización:

```swift
let estadoAutorizacion = CNContactStore.authorizationStatus(for: .contacts)

switch estadoAutorizacion {
case .authorized:
    print("Acceso completo")
case .limited:
    print("Acceso limitado a contactos seleccionados")
case .denied:
    print("Acceso denegado")
case .restricted:
    print("Acceso restringido por políticas del dispositivo")
case .notDetermined:
    print("Aún no se ha solicitado permiso")
@unknown default:
    print("Estado desconocido")
}
```

## Conceptos clave

### 1. CNContactStore

Es el **punto de entrada principal** al framework. Actúa como intermediario entre tu aplicación y la base de datos de contactos del sistema. A través de él solicitas permisos, ejecutas consultas, y guardas cambios.

```swift
let store = CNContactStore()
```

### 2. CNContact y CNMutableContact

`CNContact` es un objeto **inmutable** que representa un contacto. Contiene propiedades como `givenName`, `familyName`, `phoneNumbers`, `emailAddresses`, etc. Para modificar un contacto, se utiliza `CNMutableContact` o se obtiene una copia mutable con `mutableCopy()`.

### 3. CNKeyDescriptor y Fetch Keys

Por motivos de rendimiento y privacidad, Contacts **no carga todas las propiedades** de un contacto automáticamente. Debes especificar exactamente qué propiedades necesitas mediante *key descriptors*:

```swift
let claves: [CNKeyDescriptor] = [
    CNContactGivenNameKey as CNKeyDescriptor,
    CNContactFamilyNameKey as CNKeyDescriptor,
    CNContactPhoneNumbersKey as CNKeyDescriptor
]
```

> Si intentas acceder a una propiedad que no solicitaste, la app lanzará una excepción en tiempo de ejecución.

### 4. CNContactFetchRequest

Objeto que encapsula los criterios de búsqueda para obtener contactos. Permite especificar las claves a recuperar, predicados de filtrado y opciones de ordenación.

### 5. CNSaveRequest

Agrupa una o más operaciones de escritura (crear, actualizar, eliminar) en una sola transacción atómica. Esto garantiza que todas las operaciones se ejecuten exitosamente o ninguna se aplique.

### 6. CNLabeledValue

Muchas propiedades de un contacto (teléfonos, emails, direcciones) son arrays de `CNLabeledValue`, que asocian un **valor** con una **etiqueta** (casa, trabajo, móvil, etc.). Esto permite que un contacto tenga múltiples teléfonos, cada uno con su tipo correspondiente.

```swift
// Un número de teléfono con etiqueta "móvil"
let telefono = CNLabeledValue(
    label: CNLabelPhoneNumberMobile,
    value: CNPhoneNumber(stringValue: "+34 612 345 678")
)
```

## Ejemplo básico

Este ejemplo muestra cómo obtener todos los contactos y mostrar su nombre y número de teléfono:

```swift
import Contacts

/// Obtiene todos los contactos del dispositivo con nombre y teléfono
func obtenerTodosLosContactos() {
    let store = CNContactStore()

    // Definir las propiedades que queremos recuperar
    let clavesARecuperar: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor,
        CNContactPhoneNumbersKey as CNKeyDescriptor
    ]

    // Crear la solicitud de búsqueda
    let solicitud = CNContactFetchRequest(keysToFetch: clavesARecuperar)
    solicitud.sortOrder = .givenName // Ordenar por nombre

    do {
        // Iterar sobre todos los contactos que coincidan
        try store.enumerateContacts(with: solicitud) { contacto, punteroDetener in
            let nombreCompleto = "\(contacto.givenName) \(contacto.familyName)"

            // Extraer todos los números de teléfono del contacto
            let telefonos = contacto.phoneNumbers.map { $0.value.stringValue }

            print("📇 \(nombreCompleto): \(telefonos.joined(separator: ", "))")
        }
    } catch {
        print("❌ Error al obtener contactos: \(error.localizedDescription)")
    }
}
```

## Ejemplo intermedio

Este ejemplo implementa un servicio completo de gestión de contactos con operaciones CRUD:

```swift
import Contacts

/// Servicio de gestión de contactos con operaciones CRUD completas
class ServicioContactos {

    private let store = CNContactStore()

    // MARK: - Verificación de permisos

    /// Verifica y solicita permisos de acceso a contactos
    func verificarPermisos() async -> Bool {
        let estado = CNContactStore.authorizationStatus(for: .contacts)

        switch estado {
        case .authorized, .limited:
            return true
        case .notDetermined:
            // Solicitar permiso de forma asíncrona
            do {
                return try await store.requestAccess(for: .contacts)
            } catch {
                print("❌ Error al solicitar permisos: \(error)")
                return false
            }
        case .denied, .restricted:
            return false
        @unknown default:
            return false
        }
    }

    // MARK: - Búsqueda de contactos

    /// Busca contactos por nombre usando un predicado
    func buscarContactos(nombre: String) throws -> [CNContact] {
        let clavesARecuperar: [CNKeyDescriptor] = [
            CNContactGivenNameKey as CNKeyDescriptor,
            CNContactFamilyNameKey as CNKeyDescriptor,
            CNContactEmailAddressesKey as CNKeyDescriptor,
            CNContactPhoneNumbersKey as CNKeyDescriptor,
            CNContactImageDataAvailableKey as CNKeyDescriptor,
            CNContactThumbnailImageDataKey as CNKeyDescriptor,
            CNContactOrganizationNameKey as CNKeyDescriptor
        ]

        // Crear predicado para buscar por nombre
        let predicado = CNContact.predicateForContacts(matchingName: nombre)

        // Ejecutar la búsqueda
        let contactos = try store.unifiedContacts(
            matching: predicado,
            keysToFetch: clavesARecuperar
        )

        return contactos
    }

    // MARK: - Creación de contactos

    /// Crea un nuevo contacto con los datos proporcionados
    func crearContacto(
        nombre: String,
        apellido: String,
        telefono: String,
        email: String,
        empresa: String? = nil
    ) throws {
        let nuevoContacto = CNMutableContact()

        // Configurar datos básicos
        nuevoContacto.givenName = nombre
        nuevoContacto.familyName = apellido

        // Agregar número de teléfono con etiqueta "móvil"
        let valorTelefono = CNLabeledValue(
            label: CNLabelPhoneNumberMobile,
            value: CNPhoneNumber(stringValue: telefono)
        )
        nuevoContacto.phoneNumbers = [valorTelefono]

        // Agregar email con etiqueta "personal"
        let valorEmail = CNLabeledValue(
            label: CNLabelHome,
            value: email as NSString
        )
        nuevoContacto.emailAddresses = [valorEmail]

        // Agregar empresa si se proporciona
        if let empresa = empresa {
            nuevoContacto.organizationName = empresa
        }

        // Crear solicitud de guardado y ejecutar
        let solicitudGuardado = CNSaveRequest()
        solicitudGuardado.add(nuevoContacto, toContainerWithIdentifier: nil)

        try store.execute(solicitudGuardado)
        print("✅ Contacto '\(nombre) \(apellido)' creado exitosamente")
    }

    // MARK: - Actualización de contactos

    /// Actualiza el teléfono de un contacto existente
    func actualizarTelefono(
        contacto: CNContact,
        nuevoTelefono: String
    ) throws {
        // Obtener copia mutable del contacto
        guard let contactoMutable = contacto.mutableCopy() as? CNMutableContact else {
            throw NSError(
                domain: "ServicioContactos",
                code: 1,
                userInfo: [NSLocalizedDescriptionKey: "No se pudo obtener copia mutable"]
            )
        }

        // Reemplazar los teléfonos existentes con el nuevo
        let nuevoValorTelefono = CNLabeledValue(
            label: CNLabelPhoneNumberMobile,
            value: CNPhoneNumber(stringValue: nuevoTelefono)
        )
        contactoMutable.phoneNumbers = [nuevoValorTelefono]

        // Guardar cambios
        let solicitudGuardado = CNSaveRequest()
        solicitudGuardado.update(contactoMutable)

        try store.execute(solicitudGuardado)
        print("✅ Teléfono actualizado exitosamente")
    }

    // MARK: - Eliminación de contactos

    /// Elimina un contacto de la agenda
    func eliminarContacto(_ contacto: CNContact) throws {
        guard let contactoMutable = contacto.mutableCopy() as? CNMutableContact else {
            throw NSError(
                domain: "ServicioContactos",
                code: 2,
                userInfo: [NSLocalizedDescriptionKey: "No se pudo obtener copia mutable"]
            )
        }

        let solicitudGuardado = CNSaveRequest()
        solicitudGuardado.delete(contactoMutable)

        try store.execute(solicitudGuardado)
        print("🗑️ Contacto eliminado exitosamente")
    }

    // MARK: - Obtener contactos con filtro personalizado

    /// Obtiene contactos que tienen email de una empresa específica
    func contactosPorDominioEmail(dominio: String) throws -> [CNContact] {
        let clavesARecuperar: [CNKeyDescriptor] = [
            CNContactGivenNameKey as CNKeyDescriptor,
            CNContactFamilyNameKey as CNKeyDescriptor,
            CNContactEmailAddressesKey as CNKeyDescriptor
        ]

        var contactosFiltrados: [CNContact] = []
        let solicitud = CNContactFetchRequest(keysToFetch: clavesARecuperar)

        try store.enumerateContacts(with: solicitud) { contacto, _ in
            // Verificar si algún email contiene el dominio buscado
            let tieneEmailDominio = contacto.emailAddresses.contains { labeledValue in
                let email = labeledValue.value as String
                return email.lowercased().hasSuffix("@\(dominio.lowercased())")
            }

            if tieneEmailDominio {
                contactosFiltrados.append(contacto)
            }
        }

        return contactosFiltrados
    }
}
```

## Ejemplo avanzado

Este ejemplo implementa una arquitectura **MVVM** completa con SwiftUI, Combine y manejo robusto de estados:

```swift
import SwiftUI
import Contacts
import Combine

// MARK: - Modelo de dominio

/// Modelo limpio que desacopla la capa de datos del framework Contacts
struct ContactoModelo: Identifiable,