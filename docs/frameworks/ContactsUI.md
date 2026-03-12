---
sidebar_position: 1
title: ContactsUI
---

# ContactsUI

## ¿Qué es ContactsUI?

**ContactsUI** es un framework de Apple que proporciona controladores de vista prediseñados para mostrar, seleccionar, crear y editar contactos dentro de una aplicación iOS. Actúa como la capa de interfaz de usuario del framework `Contacts`, permitiendo a los desarrolladores integrar funcionalidades de gestión de contactos sin necesidad de construir interfaces personalizadas desde cero. Este framework garantiza una experiencia de usuario coherente con la aplicación nativa de Contactos de Apple.

El framework resulta especialmente valioso porque abstrae toda la complejidad de renderizar la información de contacto, manejar la navegación entre campos (teléfono, correo, dirección, foto, etc.) y gestionar la edición de datos. Al utilizar los controladores que ofrece ContactsUI, el desarrollador se beneficia automáticamente de las actualizaciones de diseño que Apple implementa en cada versión de iOS, manteniendo la aplicación alineada con las guías de interfaz humana (HIG).

Es importante distinguir entre `Contacts` y `ContactsUI`: el primero maneja el acceso y manipulación de datos de contactos a nivel de modelo, mientras que el segundo ofrece las vistas listas para presentar esos datos al usuario. En la mayoría de aplicaciones que necesitan interactuar con contactos, se utilizan ambos frameworks en conjunto. ContactsUI está disponible desde **iOS 9** y es compatible con iPadOS, macOS (a través de Catalyst) y parcialmente con watchOS.

## Casos de uso principales

- **Selector de contactos en apps de mensajería**: Permite al usuario elegir uno o varios contactos de su agenda para enviarles un mensaje, invitación o compartir contenido, utilizando `CNContactPickerViewController`.

- **Visualización de perfil de contacto**: Muestra la ficha completa de un contacto con todos sus datos (nombre, teléfonos, correos, direcciones, foto) mediante `CNContactViewController`, ideal para apps de CRM o directorios empresariales.

- **Creación de nuevos contactos desde la app**: Cuando la aplicación recibe información de contacto (por ejemplo, escaneando una tarjeta de presentación o leyendo un código QR), puede presentar la interfaz de creación de contacto prellenada con los datos obtenidos.

- **Edición de contactos existentes**: Apps que gestionan clientes o proveedores pueden permitir al usuario editar directamente la información de un contacto almacenado en la agenda del dispositivo.

- **Selección de propiedades específicas**: Permite al usuario seleccionar un dato particular de un contacto (por ejemplo, solo un número de teléfono o una dirección de correo) en lugar del contacto completo, útil para apps que necesitan un dato puntual.

- **Integración en flujos de onboarding**: Durante el registro de un usuario, se puede ofrecer la opción de autocompletar datos personales seleccionando su propio contacto de la agenda.

## Instalación y configuración

### Agregar el framework al proyecto

ContactsUI viene incluido en el SDK de iOS, por lo que no requiere instalación mediante gestores de dependencias. Solo necesitas importarlo:

```swift
import ContactsUI
import Contacts // Generalmente necesario para trabajar con los modelos de datos
```

### Permisos en Info.plist

Para acceder a los contactos del usuario, es **obligatorio** declarar la clave de privacidad en el archivo `Info.plist`:

```xml
<key>NSContactsUsageDescription</key>
<string>Necesitamos acceso a tus contactos para que puedas compartir información con ellos.</string>
```

> **Nota importante**: `CNContactPickerViewController` es una excepción especial. Este controlador se ejecuta en un proceso separado (*out-of-process*) y **no requiere** que el usuario otorgue permiso de acceso a contactos. La app solo recibe los contactos que el usuario selecciona explícitamente. Sin embargo, si usas `CNContactViewController` o accedes directamente al `CNContactStore`, sí necesitarás el permiso.

### Solicitar permisos programáticamente

```swift
import Contacts

func solicitarPermisoContactos() {
    let store = CNContactStore()
    
    store.requestAccess(for: .contacts) { concedido, error in
        DispatchQueue.main.async {
            if concedido {
                print("✅ Permiso concedido para acceder a contactos")
            } else {
                print("❌ Permiso denegado: \(error?.localizedDescription ?? "Sin detalle")")
            }
        }
    }
}
```

### Compatibilidad con iOS 18+

A partir de iOS 18, Apple introdujo **acceso limitado a contactos**, donde el usuario puede seleccionar solo ciertos contactos a los que la app tendrá acceso. Es fundamental manejar este caso:

```swift
import Contacts

func verificarNivelAcceso() {
    let status = CNContactStore.authorizationStatus(for: .contacts)
    
    switch status {
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
        break
    }
}
```

## Conceptos clave

### 1. CNContactPickerViewController

Es el controlador principal para **seleccionar contactos**. Se ejecuta fuera del proceso de la app (*out-of-process*), lo que significa que el usuario puede navegar por todos sus contactos sin que la app tenga acceso directo a la agenda. Solo se comparten con la app los contactos que el usuario selecciona explícitamente. Esto lo convierte en la opción más respetuosa con la privacidad.

### 2. CNContactViewController

Controlador diseñado para **mostrar, crear o editar** un contacto individual. Ofrece tres modos de operación principales:
- `init(for: CNContact)` → Visualización de un contacto existente.
- `init(forNewContact: CNContact?)` → Creación de un contacto nuevo (opcionalmente prellenado).
- `init(forUnknownContact: CNContact)` → Presentación de un contacto desconocido con opción de agregarlo a la agenda.

### 3. CNContactPickerDelegate

Protocolo delegado que define los métodos de callback para `CNContactPickerViewController`. Permite responder a eventos como la selección de un contacto completo, la selección de una propiedad específica, la selección múltiple o la cancelación del picker.

### 4. CNContact y CNMutableContact

`CNContact` es la clase inmutable que representa un contacto con todas sus propiedades (nombre, teléfonos, correos, etc.). `CNMutableContact` es su contraparte editable, utilizada para crear o modificar contactos antes de guardarlos.

### 5. CNContactProperty

Representa una **propiedad específica** seleccionada por el usuario dentro de un contacto. Por ejemplo, si configuras el picker para seleccionar números de teléfono, recibirás un `CNContactProperty` que contiene tanto el contacto como el valor del teléfono seleccionado.

### 6. CNContactStore

Aunque pertenece al framework `Contacts` (no a ContactsUI), es esencial comprenderlo. Es el punto de acceso centralizado para leer, crear, actualizar y eliminar contactos del almacén de contactos del dispositivo. Muchas operaciones de ContactsUI requieren interactuar con él.

## Ejemplo básico

Este ejemplo muestra cómo presentar el selector de contactos y obtener el contacto seleccionado:

```swift
import UIKit
import ContactsUI

/// Controlador básico que presenta un selector de contactos
class SelectorContactoBasicoVC: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        
        // Crear botón para abrir el selector
        let boton = UIButton(type: .system)
        boton.setTitle("Seleccionar Contacto", for: .normal)
        boton.titleLabel?.font = .preferredFont(forTextStyle: .headline)
        boton.addTarget(self, action: #selector(abrirSelectorContactos), for: .touchUpInside)
        boton.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(boton)
        NSLayoutConstraint.activate([
            boton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            boton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    @objc private func abrirSelectorContactos() {
        // Crear el picker de contactos (no requiere permiso previo)
        let picker = CNContactPickerViewController()
        picker.delegate = self
        
        // Presentar el picker de forma modal
        present(picker, animated: true)
    }
}

// MARK: - CNContactPickerDelegate
extension SelectorContactoBasicoVC: CNContactPickerDelegate {
    
    /// Se llama cuando el usuario selecciona un contacto
    func contactPicker(_ picker: CNContactPickerViewController,
                       didSelect contact: CNContact) {
        // Extraer nombre completo del contacto
        let nombre = CNContactFormatter.string(from: contact,
                                                style: .fullName) ?? "Sin nombre"
        
        // Obtener el primer número de teléfono si existe
        let telefono = contact.phoneNumbers.first?.value.stringValue ?? "Sin teléfono"
        
        print("📱 Contacto seleccionado: \(nombre) - \(telefono)")
    }
    
    /// Se llama cuando el usuario cancela la selección
    func contactPickerDidCancel(_ picker: CNContactPickerViewController) {
        print("🚫 El usuario canceló la selección de contacto")
    }
}
```

## Ejemplo intermedio

Este ejemplo muestra cómo filtrar contactos, seleccionar propiedades específicas y crear nuevos contactos:

```swift
import UIKit
import ContactsUI
import Contacts

/// Controlador que demuestra funcionalidades intermedias de ContactsUI:
/// - Filtrado de contactos con predicados
/// - Selección de propiedades específicas (solo emails)
/// - Creación de nuevos contactos prellenados
class GestionContactosVC: UIViewController {
    
    // MARK: - Propiedades
    
    private let stackView: UIStackView = {
        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 16
        stack.translatesAutoresizingMaskIntoConstraints = false
        return stack
    }()
    
    private let etiquetaResultado: UILabel = {
        let label = UILabel()
        label.textAlignment = .center
        label.numberOfLines = 0
        label.font = .preferredFont(forTextStyle: .body)
        label.textColor = .secondaryLabel
        label.text = "Selecciona una opción"
        return label
    }()
    
    // MARK: - Ciclo de vida
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Gestión de Contactos"
        view.backgroundColor = .systemBackground
        configurarInterfaz()
    }
    
    // MARK: - Configuración de UI
    
    private func configurarInterfaz() {
        view.addSubview(stackView)
        
        NSLayoutConstraint.activate([
            stackView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            stackView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            stackView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 32),
            stackView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -32)
        ])
        
        // Botón 1: Seleccionar solo el email de un contacto
        let botonEmail = crearBoton(titulo: "📧 Seleccionar Email",
                                     accion: #selector(seleccionarEmail))
        
        // Botón 2: Seleccionar múltiples contactos
        let botonMultiples = crearBoton(titulo: "👥 Selección Múltiple",
                                         accion: #selector(seleccionarMultiples))
        
        // Botón 3: Crear nuevo contacto prellenado
        let botonNuevo = crearBoton(titulo: "➕ Crear Contacto Nuevo",
                                     accion: #selector(crearContactoNuevo))
        
        // Botón 4: Ver contacto existente
        let botonVer = crearBoton(titulo: "👤 Ver Contacto",
                                   accion: #selector(verContactoExistente))
        
        [botonEmail, botonMultiples, botonNuevo, botonVer, etiquetaResultado]
            .forEach { stackView.addArrangedSubview($0) }
    }
    
    private func crearBoton(titulo: String, accion: Selector) -> UIButton {
        let boton = UIButton(type: .system)
        boton.setTitle(titulo, for: .normal)
        boton.titleLabel?.font = .preferredFont(forTextStyle: .headline)
        boton.addTarget(self, action: accion, for: .touchUpInside)
        boton.heightAnchor.constraint(equalToConstant: 44).isActive = true
        return boton
    }
    
    // MARK: - Acciones
    
    /// Abre el picker configurado para seleccionar SOLO un email
    @objc private func seleccionarEmail() {
        let picker = CNContactPickerViewController()
        picker.delegate = self
        
        // Filtrar: solo mostrar contactos que tengan al menos un email
        picker.predicateForEnablingContact = NSPredicate(
            format: "emailAddresses.@count > 0"
        )
        
        // Configurar para que al tocar un contacto se seleccione una propiedad
        picker.displayedPropertyKeys = [CNContactEmailAddressesKey]
        
        // Indicar qué propiedades permiten selección directa
        picker.predicateForSelectionOfProperty = NSPredicate(
            format: "key == 'emailAddresses'"
        )
        
        present(picker, animated: true)
    }
    
    /// Abre el picker en modo de selección múltiple
    @objc private func seleccionarMultiples() {
        let picker = CNContactPickerViewController()
        picker.delegate = self
        
        // Al NO implementar didSelect(contact:) singular,
        // el picker automáticamente permite selección múltiple
        present(picker, animated: true)
    }
    
    /// Crea un nuevo contacto con datos prellenados
    @objc private func crearContactoNuevo() {
        // Crear un contacto mutable con datos iniciales
        let contactoNuevo = CNMutableContact()
        contactoNuevo.givenName = "Carlos"
        contactoNuevo.familyName = "García"
        contactoNuevo.organizationName = "Mi Empresa S.A."
        
        // Agregar un teléfono prellenado
        let telefono = CNLabeledValue(
            label: CNLabelPhoneNumberMobile,
            value: CNPhoneNumber(stringValue: "+34 612 345 678")
        )
        contactoNuevo.phoneNumbers = [telefono]
        
        // Agregar un email prellenado
        let email = CNLabeledValue(