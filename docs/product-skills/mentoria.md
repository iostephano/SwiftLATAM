---
sidebar_position: 1
title: Mentoria
---

# Mentoría en el Desarrollo iOS

## ¿Qué es la mentoría técnica?

La mentoría es una relación profesional en la que una persona con mayor experiencia (mentor/a) guía, aconseja y acompaña a otra persona (mentee) en su crecimiento técnico, profesional y personal. No se trata simplemente de "enseñar a programar": es un proceso bidireccional donde ambas partes aprenden, crecen y construyen una red de confianza.

En el contexto del desarrollo iOS, la mentoría abarca desde la revisión de código y decisiones de arquitectura hasta la navegación de entrevistas técnicas, la negociación salarial y la construcción de una carrera sostenible en tecnología.

## ¿Por qué es crucial para un dev iOS en LATAM?

El ecosistema iOS en Latinoamérica tiene características únicas que hacen que la mentoría sea especialmente valiosa:

### 1. Brecha de acceso a información de calidad
Gran parte del contenido avanzado sobre iOS está en inglés y orientado a mercados como Silicon Valley. Un/a mentor/a local puede contextualizar ese conocimiento a la realidad latinoamericana: mercados más pequeños, presupuestos diferentes, equipos con menos recursos y oportunidades de trabajo remoto para empresas internacionales.

### 2. Comunidades en crecimiento
Las comunidades iOS en ciudades como Ciudad de México, Buenos Aires, Bogotá, São Paulo, Santiago y Lima están creciendo, pero aún son más pequeñas que sus equivalentes en EE.UU. o Europa. Cada mentor/a que forma nuevos desarrolladores multiplica el impacto en toda la región.

### 3. Trabajo remoto y empresas internacionales
Muchos devs iOS en LATAM trabajan para empresas de EE.UU. o Europa. Un/a mentor/a que ya haya transitado ese camino puede orientar sobre diferencias culturales, expectativas de comunicación, zonas horarias y estándares de calidad.

### 4. Síndrome del impostor
Es común sentir que "no estamos al nivel" cuando nos comparamos con perfiles de desarrolladores en países con ecosistemas más maduros. La mentoría ayuda a construir confianza real, basada en progreso medible y retroalimentación honesta.

## Los dos roles: ser mentee y ser mentor/a

### Como mentee (aprendiz)

Ser un buen mentee es una habilidad en sí misma. No se trata de esperar que alguien te dé todas las respuestas, sino de llegar preparado/a con preguntas específicas y contexto claro.

#### Ejemplo práctico: preparar una sesión de mentoría

Imagina que estás trabajando en tu primera app y tienes dudas sobre arquitectura. En lugar de preguntar *"¿qué arquitectura debería usar?"*, prepara un documento como este:

```swift
// CONTEXTO: Estoy construyendo una app de seguimiento de hábitos
// SITUACIÓN ACTUAL: Tengo toda la lógica en los ViewControllers
// PROBLEMA: El código es difícil de testear y los VCs tienen 500+ líneas

// Ejemplo de mi código actual (problemático):
class HabitListViewController: UIViewController {
    var habits: [Habit] = []
    
    func loadHabits() {
        // Lógica de red directamente en el VC
        let url = URL(string: "https://api.example.com/habits")!
        URLSession.shared.dataTask(with: url) { [weak self] data, _, error in
            guard let data = data else { return }
            // Decodificación directamente en el VC
            let habits = try? JSONDecoder().decode([Habit].self, from: data)
            DispatchQueue.main.async {
                self?.habits = habits ?? []
                self?.tableView.reloadData()
                // Lógica de negocio también aquí
                self?.calculateStreak()
                self?.updateBadges()
                self?.scheduleNotifications()
            }
        }.resume()
    }
    
    // PREGUNTA ESPECÍFICA PARA MI MENTOR/A:
    // He leído sobre MVVM y VIPER. Dado que:
    // - Soy el único dev en el proyecto
    // - La app tiene 6 pantallas
    // - Quiero aprender a testear
    // ¿Qué patrón me recomendarías y por qué?
}
```

La diferencia entre una pregunta genérica y una contextualizada puede ser la diferencia entre una sesión productiva y una conversación superficial.

#### Protocolo para ser un mentee efectivo

Podemos modelar este comportamiento incluso en código, como ejercicio conceptual:

```swift
// Un "protocolo" para ser un buen mentee
protocol EffectiveMentee {
    var currentGoals: [Goal] { get }
    var blockers: [Blocker] { get }
    var questionsForNextSession: [Question] { get }
    
    func prepareForSession() -> SessionAgenda
    func applyFeedback(_ feedback: Feedback) -> ActionPlan
    func reportProgress() -> ProgressReport
}

struct Goal {
    let description: String
    let deadline: Date
    let measurableOutcome: String
    
    // Ejemplo de meta bien definida:
    // description: "Implementar MVVM en la pantalla de hábitos"
    // deadline: 2 semanas
    // measurableOutcome: "VC con menos de 100 líneas, ViewModel con tests unitarios"
}

struct Question {
    let topic: String
    let context: String
    let whatIveTriedSoFar: String  // CLAVE: siempre mostrar lo que ya intentaste
    let specificAsk: String
}

struct SessionAgenda {
    let progressSinceLastSession: String
    let currentBlockers: [Blocker]
    let prioritizedQuestions: [Question]  // Máximo 3 por sesión
    let timeEstimate: TimeInterval
}
```

### Como mentor/a

No necesitas 10 años de experiencia para ser mentor/a. Si llevas 2 años desarrollando en iOS y alguien está empezando, tienes mucho que ofrecer. La mentoría no es sobre ser experto/a en todo, sino sobre compartir lo que ya sabes y ser honesto/a sobre lo que no.

#### Framework para una sesión de code review como mentoría

```swift
// Framework para dar retroalimentación constructiva en code reviews
enum FeedbackType {
    case mustFix       // Bugs, crashes, memory leaks
    case shouldImprove // Mejor práctica que evitará problemas futuros
    case suggestion    // "Nice to have", estilo, convenciones
    case praise        // ¡Lo que está bien hecho! Crucial para la motivación
}

struct CodeReviewComment {
    let type: FeedbackType
    let line: Int
    let comment: String
    let explanation: String    // El POR QUÉ es más importante que el QUÉ
    let resource: URL?         // Link a documentación o artículo relevante
    let alternativeCode: String?
}

// EJEMPLO REAL de feedback constructivo:
let goodFeedback = CodeReviewComment(
    type: .shouldImprove,
    line: 42,
    comment: "Considera usar [weak self] en este closure",
    explanation: """
    Este closure es retenido por URLSession y a su vez captura 'self' 
    (el ViewController). Esto crea un ciclo de retención: el VC retiene 
    a URLSession (indirectamente), y el closure retiene al VC.
    
    Si el usuario navega hacia atrás antes de que la request termine,
    el VC no se liberará de memoria. Con el tiempo, esto puede causar
    un memory leak significativo.
    
    Herramienta útil: usa el Memory Graph Debugger en Xcode 
    (Debug > Debug Memory Graph) para visualizar estos ciclos.
    """,
    resource: URL(string: "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/automaticreferencecounting/"),
    alternativeCode: """
    URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
        guard let self = self else { return }
        // ahora puedes usar self de forma segura
    }
    """
)
```

#### La técnica del "No te doy el pez, te enseño a pescar"

```swift
// ❌ Mentor/a que da la respuesta directa:
// "Usa MVVM. Aquí está el código. Cópialo."

// ✅ Mentor/a que guía el descubrimiento:
struct MentoringApproach {
    
    /// En lugar de dar la respuesta, guiar con preguntas
    func guideMenteeToSolution(problem: String) -> [String] {
        return [
            // 1. Entender el problema real
            "¿Qué es exactamente lo que está fallando? ¿Puedes reproducirlo?",
            
            // 2. Explorar lo que ya saben
            "¿Qué has intentado hasta ahora? ¿Qué resultado obtuviste?",
            
            // 3. Orientar la investigación
            "¿Qué pasa si pones un breakpoint en la línea 42? ¿Qué valor tiene esa variable?",
            
            // 4. Conectar con conceptos fundamentales
            "Esto está relacionado con el ciclo de vida del ViewController. ¿Recuerdas en qué orden se llaman viewDidLoad, viewWillAppear y viewDidAppear?",
            
            // 5. Validar y reforzar
            "¡Exacto! Ahora, ¿cómo podrías escribir un test que verifique este comportamiento?"
        ]
    }
}
```

## Pasos accionables para empezar HOY

### Si buscas un/a mentor/a:

1. **Define qué necesitas específicamente.** ¿Prepararte para entrevistas? ¿Mejorar tu arquitectura? ¿Transicionar de Android a iOS? ¿Conseguir tu primer trabajo remoto?

2. **Participa activamente en comunidades.** Únete a:
   - **NSCoder México / Argentina / Colombia**: meetups locales de desarrollo Apple
   - **Canales de Slack/Discord** de comunidades iOS hispanohablantes
   - **Twitter/X**: sigue a devs iOS de LATAM, interactúa con su contenido, haz preguntas inteligentes
   - **GitHub**: contribuye a proyectos open source y pide reviews

3. **Ofrece algo a cambio.** La mentoría no tiene que ser unidireccional. Puedes ofrecer:
   - Ayudar con documentación o traducciones
   - Dar feedback como usuario/a de sus apps o herramientas
   - Compartir tu perspectiva fresca (a veces un/a junior ve problemas que un/a senior ya normalizó)

4. **Estructura el proceso.** Propón reuniones regulares (quincenal suele funcionar bien), con agenda definida y duración acotada (30-45 minutos).

5. **Lleva un registro de tu progreso.** Usa algo simple:

```swift
// Herramienta simple para trackear tu progreso como mentee
struct MentorshipJournal {
    struct Entry: Codable {
        let date: Date
        let sessionNumber: Int
        let topicsDiscussed: [String]
        let keyLearnings: [String]
        let actionItems: [ActionItem]
        let blockerResolved: Bool
    }
    
    struct ActionItem: Codable {
        let description: String
        let deadline: Date
        var isCompleted: Bool
        
        // Ejemplo:
        // description: "Refactorizar HabitListVC usando MVVM"
        // deadline: próxima sesión (2 semanas)
        // isCompleted: false → ¿lo completaste antes de la siguiente sesión?
    }
    
    var entries: [Entry] = []
    
    /// Métrica clave: ¿estás completando tus action items?
    var completionRate: Double {
        let allItems = entries.flatMap { $0.actionItems }
        guard !allItems.isEmpty else { return 0 }
        let completed = allItems.filter { $0.isCompleted }.count
        return Double(completed) / Double(allItems.count)
    }
    
    /// Si tu completion rate es menor al 50%, algo no está funcionando
    var needsAdjustment: Bool {
        completionRate < 0.5 && entries.count >= 3
    }
}
```

### Si quieres ser mentor/a:

1. **Empieza con una persona.** No necesitas crear un programa formal. Identifica a alguien en tu equipo o comunidad que pueda beneficiarse de tu experiencia.

2. **Establece expectativas claras.** Define desde el inicio:
   - Frecuencia y duración de las sesiones
   - Canales de comunicación (¿puede escribirte por Slack en cualquier momento o solo en horario laboral?)
   - Duración del compromiso (3 meses es un buen período inicial)

3. **Practica la escucha activa.** A veces el mentee no necesita una solución técnica, sino validación, perspectiva o simplemente alguien que le diga "sí, eso es normal, yo también pasé por eso".

4. **Documenta patrones comunes.** Si tres mentees te preguntan lo mismo, escribe un artículo o crea un recurso. Así multiplicas tu impacto.

5. **Aprende a decir "no sé".** La honestidad construye más confianza que fingir omnisciencia. "No sé, pero investiguemos juntos" es una respuesta perfectamente válida y extraordinariamente poderosa.

## Mentoría dentro de equipos: Code Reviews como herramienta

Una de las formas más efectivas de mentoría en el día a día es a través de code reviews bien hechos. No se trata solo de aprobar o rechazar PRs, sino de convertir cada review en una oportunidad de aprendizaje:

```swift
// Ejemplo: Un junior envía este código en un PR

// CÓDIGO DEL JUNIOR:
class NetworkManager {
    static let shared = NetworkManager()
    
    func fetchHabits(completion: @escaping ([Habit]) -> Void) {
        let url = URL(string: "https://api.example.com/habits")!
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data {
                let habits = try! JSONDecoder().decode([Habit].self, from: data)
                completion(habits)
            }
        }.resume()
    }
}

// REVIEW DE MENTORÍA (no solo "esto está mal"):

// 🟡 Línea 1: El singleton funciona aquí, pero ¿has considerado 
//    cómo vas a testear los ViewModels que dependan de esto?
//    Pista: busca "Dependency Injection vs Singleton" 
//    → Te dejo este recurso: [link]

// 🔴 Línea 7: `try!` va a crashear la app si el JSON no tiene 
//    el formato esperado. Esto PASARÁ en producción eventualmente.
//    ¿Qué pasa si el backend agrega un campo o cambia un tipo?
//    Acción: usa do-catch y maneja el error.

// 🔴 Línea 5: `URL(string:)!` también puede crashear.
//    Aunque la URL es hardcoded y "siempre va a funcionar",
//    es un hábito peligroso. Acostúmbrate a manejar opcionales.

// 