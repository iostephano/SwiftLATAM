---
sidebar_position: 1
title: Comunicacion Tecnica
---

# Comunicación Técnica para Desarrolladores iOS

## ¿Qué es la Comunicación Técnica?

La comunicación técnica es la habilidad de **transmitir ideas complejas de forma clara, estructurada y adaptada a tu audiencia**. No se trata solo de hablar sobre código; se trata de que la otra persona —sea un colega, un PM, un diseñador o un cliente— entienda exactamente lo que necesita entender, sin ruido, sin ambigüedad.

Para un desarrollador iOS, esto abarca desde cómo nombras una variable hasta cómo explicas en un standup por qué una feature va a tardar tres días más de lo estimado.

> **"El código se escribe una vez, pero se lee cientos de veces."**
> La comunicación técnica empieza en tu editor de código y termina en la sala de reuniones.

---

## ¿Por Qué es Crucial para un Dev iOS en LATAM?

En el contexto latinoamericano, la comunicación técnica tiene dimensiones particulares que la hacen aún más relevante:

### 1. Trabajo remoto con equipos distribuidos
La mayoría de las oportunidades bien remuneradas para devs iOS en LATAM involucran equipos en Estados Unidos, Canadá o Europa. Tu capacidad de comunicar en inglés **y** en español, de forma escrita y oral, determina directamente tu crecimiento profesional.

### 2. Diferencias culturales
En muchas culturas latinoamericanas existe la tendencia a **evitar el conflicto** o a no decir "no sé" directamente. En equipos técnicos, esta ambigüedad genera bugs, retrasos y frustración. Aprender a comunicar con claridad y honestidad es una ventaja competitiva brutal.

### 3. La brecha entre lo técnico y el negocio
Muchas startups y empresas en LATAM tienen equipos pequeños donde el dev iOS también debe hablar con stakeholders no técnicos. Si no puedes traducir "necesitamos refactorizar la capa de networking para adoptar async/await" a algo que un CEO entienda, ese refactor nunca va a ser priorizado.

### 4. Code reviews como herramienta de crecimiento
En equipos remotos, los Pull Requests son tu carta de presentación diaria. Un PR bien escrito comunica competencia, profesionalismo y respeto por el tiempo de los demás.

---

## Las 5 Dimensiones de la Comunicación Técnica

### 📝 1. Código como Comunicación

Tu código **es** comunicación. Cada nombre de función, cada estructura, cada comentario le habla a quien lo lee después —que muchas veces eres tú mismo, seis meses después.

#### ❌ Código que no comunica

```swift
func process(_ d: [String: Any]) -> Bool {
    guard let x = d["s"] as? Int else { return false }
    if x > 0 && x < 100 {
        let r = x * 2
        UserDefaults.standard.set(r, forKey: "v")
        return true
    }
    return false
}
```

¿Qué hace esta función? ¿Qué es `d`? ¿Qué significa `"s"`? ¿Por qué multiplicamos por 2? ¿Qué es `"v"`?

#### ✅ Código que comunica

```swift
/// Valida y almacena la puntuación del usuario después de aplicar el multiplicador de bonificación.
/// - Parameter scorePayload: Diccionario que contiene la puntuación bajo la clave "score".
/// - Returns: `true` si la puntuación fue válida y se almacenó correctamente.
func processAndStoreScore(from scorePayload: [String: Any]) -> Bool {
    guard let rawScore = scorePayload["score"] as? Int else {
        Logger.warning("Payload de puntuación inválido: clave 'score' no encontrada o tipo incorrecto")
        return false
    }
    
    let validScoreRange = 1...99
    guard validScoreRange.contains(rawScore) else {
        Logger.warning("Puntuación fuera de rango válido: \(rawScore)")
        return false
    }
    
    let bonusMultiplier = 2
    let finalScore = rawScore * bonusMultiplier
    
    UserDefaults.standard.set(finalScore, forKey: UserDefaultsKeys.userScore)
    Logger.info("Puntuación almacenada exitosamente: \(finalScore)")
    
    return true
}
```

**Pero podemos ir más lejos.** Un dev iOS con buena comunicación técnica eventualmente refactorizaría esto a algo con tipado fuerte:

```swift
struct ScorePayload: Decodable {
    let score: Int
    
    var isValid: Bool {
        (1...99).contains(score)
    }
    
    static let bonusMultiplier = 2
    
    var finalScore: Int {
        score * Self.bonusMultiplier
    }
}

final class ScoreService {
    
    enum ScoreError: LocalizedError {
        case invalidScore(Int)
        case decodingFailed
        
        var errorDescription: String? {
            switch self {
            case .invalidScore(let score):
                return "Puntuación fuera del rango válido: \(score). Se esperaba un valor entre 1 y 99."
            case .decodingFailed:
                return "No se pudo decodificar el payload de puntuación."
            }
        }
    }
    
    private let storage: UserDefaults
    
    init(storage: UserDefaults = .standard) {
        self.storage = storage
    }
    
    func processAndStore(_ payload: ScorePayload) throws {
        guard payload.isValid else {
            throw ScoreError.invalidScore(payload.score)
        }
        
        storage.set(payload.finalScore, forKey: UserDefaultsKeys.userScore)
    }
}
```

Nota cómo el código ahora **se explica solo**. Los errores tienen descripciones legibles. La estructura hace evidente la intención. Este es el nivel de comunicación técnica que diferencia a un developer senior.

---

### 💬 2. Pull Requests y Code Reviews

Los Pull Requests son probablemente el canal de comunicación más importante en un equipo remoto.

#### Anatomía de un PR bien comunicado

```markdown
## 🎯 ¿Qué hace este PR?

Implementa el flujo de autenticación biométrica usando Face ID / Touch ID 
como alternativa al login con contraseña.

## 🤔 ¿Por qué?

- El 73% de nuestros usuarios en México tienen dispositivos con Face ID
- Reducimos fricción en el login (de ~8 segundos a ~1 segundo)
- Requisito del sprint 14 (ticket: IOS-342)

## 🏗️ ¿Cómo?

- Nueva clase `BiometricAuthService` que encapsula `LAContext`
- Extensión de `LoginViewModel` para manejar el flujo biométrico
- Nuevo estado `.biometricPrompt` en `AuthenticationState`
- Tests unitarios para los 4 escenarios: éxito, fallo, no disponible, no enrolado

## 📸 Screenshots / Video

[Video de 15 segundos mostrando el flujo completo]

## ⚠️ Notas para el reviewer

- El método `evaluatePolicy` de `LAContext` no se puede testear directamente,
  así que creé el protocolo `BiometricEvaluating` para inyectar un mock.
- Decidí NO usar el keychain para almacenar el token biométrico en este PR.
  Eso viene en IOS-345.

## ✅ Checklist

- [x] Tests pasan en CI
- [x] Probado en dispositivo físico (iPhone 15 Pro con Face ID)
- [x] Probado escenario sin biometría (iPhone SE simulador)
- [x] Sin warnings nuevos
- [x] Accesibilidad verificada con VoiceOver
```

#### Cómo dar feedback en un Code Review

| ❌ Mal | ✅ Bien |
|--------|---------|
| "Esto está mal" | "Este approach podría causar un retain cycle porque el closure captura `self` fuertemente. ¿Qué te parece usar `[weak self]`?" |
| "¿Por qué hiciste esto?" | "Interesante approach. ¿Consideraste usar `Combine` aquí? Pregunto porque el ViewModel ya tiene publishers y podríamos mantener consistencia." |
| "Refactoriza esto" | "Sugiero extraer esta lógica a un método separado para mejorar la testeabilidad. Algo como `func validateInput(_ text: String) -> ValidationResult`" |
| "👍" | "Muy buena solución. Me gusta especialmente cómo usaste el pattern `Result` para manejar los estados de error. Aprendí algo nuevo." |

---

### 🗣️ 3. Comunicación Verbal en Reuniones

#### El framework PREP para explicar decisiones técnicas

**P**unto → **R**azón → **E**jemplo → **P**unto (repetir)

**Ejemplo en un standup:**

> **Punto:** "Propongo que migremos el networking de callbacks a async/await."
>
> **Razón:** "Actualmente tenemos 12 bugs abiertos relacionados con race conditions y retain cycles en los completion handlers. Async/await elimina ambas categorías de bugs por diseño."
>
> **Ejemplo:** "Por ejemplo, el bug IOS-287 donde el usuario ve datos viejos después de hacer pull-to-refresh. Con async/await, el flujo sería lineal y predecible."
>
> **Punto:** "Por eso recomiendo dedicar el próximo sprint a esta migración. El costo es de ~40 horas, pero estimamos que nos ahorraría ~8 horas semanales en debugging."

#### Cómo comunicar retrasos sin generar pánico

```
❌ "No voy a llegar con la feature"

✅ "La integración con el SDK de pagos está tomando más tiempo del estimado.
   El SDK tiene un bug documentado en iOS 17.2 que requiere un workaround.
   
   Tengo tres opciones:
   1. Implementar el workaround (2 días extra, solución robusta)
   2. Limitar temporalmente a iOS 17.3+ (0 días extra, afecta al 12% de usuarios)
   3. Usar un SDK alternativo (3 días extra, elimina el problema de raíz)
   
   Recomiendo la opción 1. ¿Qué opinan?"
```

---

### 📄 4. Documentación Técnica

#### Documenta el "por qué", no el "qué"

```swift
// ❌ Comentario inútil (describe el "qué", que ya es obvio)
// Establece el color de fondo a rojo
view.backgroundColor = .red

// ✅ Comentario útil (explica el "por qué")
// Usamos rojo como fondo temporal para debug de layout.
// TODO: Eliminar antes del release (IOS-400)
view.backgroundColor = .red
```

#### Architecture Decision Records (ADR)

Cuando tomas una decisión arquitectónica importante, documéntala con un ADR:

```markdown
# ADR-003: Usar SwiftUI para el módulo de Onboarding

## Estado
Aceptado (2024-01-15)

## Contexto
Necesitamos implementar un flujo de onboarding de 5 pantallas con 
animaciones y transiciones personalizadas. El equipo tiene experiencia 
mixta: 2 devs dominan UIKit, 1 domina SwiftUI.

## Decisión
Usaremos SwiftUI para el módulo de onboarding completo.

## Justificación
- El onboarding es un módulo aislado sin dependencias legacy
- Las animaciones declarativas de SwiftUI reducen el código en ~60%
- Sirve como proyecto piloto para evaluar SwiftUI antes de adoptarlo 
  en módulos más críticos
- Mínimo soporte de iOS 16+, que tiene SwiftUI estable

## Consecuencias
- Los 2 devs de UIKit necesitarán ~1 día de ramp-up
- No podremos reutilizar los componentes UIKit existentes del design system
  (crearemos wrappers con UIViewRepresentable si es necesario)
- Si la experiencia es positiva, expandiremos SwiftUI al módulo de 
  perfil en Q2

## Alternativas consideradas
1. **UIKit puro**: Más familiar, pero el código de animaciones sería 
   significativamente más complejo
2. **Híbrido UIKit + SwiftUI**: Añade complejidad de integración sin 
   beneficio claro para un módulo pequeño
```

---

### 🌐 5. Comunicación Cross-funcional

Como dev iOS, hablas con diseñadores, PMs, QA, backend y stakeholders. Cada audiencia necesita un nivel diferente de detalle.

#### El mismo problema, tres audiencias

**Al equipo de backend:**
```
"El endpoint /api/v2/user/profile está devolviendo el campo 'created_at' 
como String en formato 'MM/dd/yyyy' en lugar de ISO 8601. Esto rompe 
nuestro JSONDecoder con dateDecodingStrategy .iso8601. ¿Pueden cambiarlo 
o necesitan que hagamos un decoder custom del lado del cliente?"
```

**Al PM:**
```
"Hay una inconsistencia en cómo el servidor nos envía las fechas. 
Tenemos dos opciones: que backend lo corrija (ideal, 0 esfuerzo nuestro) 
o que nosotros lo manejemos (medio día de trabajo). Recomiendo pedirle 
a backend que lo corrija para evitar deuda técnica."
```

**Al stakeholder no técnico:**
```
"Encontramos un pequeño problema de compatibilidad entre la app y el 
servidor. Lo estamos coordinando con el equipo de backend y debería 
estar resuelto hoy. No afecta la fecha de entrega."
```

---

## Pasos Accionables: Tu Plan de 30 Días

### Semana 1: Código que comunica
- [ ] Revisa tus últimos 3 PRs: ¿Un developer nuevo entendería el contexto sin preguntarte?
- [ ] Adopta un formato estándar para tus PR descriptions
- [ ] Renombra 5 funciones o variables ambiguas en tu proyecto actual

### Semana 2: Reviews que construyen
- [ ] En tu próximo code review, usa el formato "Observación + Razón + Sugerencia"
- [ ] Prefija tus comentarios: `nit:`, `question:`, `suggestion:`, `blocker:`
- [ ] Incluye al menos un comentario positivo en cada review

### Semana 3: Documentación viva
- [ ] Escribe tu primer ADR para una decisión reciente
- [ ] Documenta el setup del proyecto en el README (que un developer nuevo pueda correr el proyecto en menos de 15 minutos)
- [ ] Agrega documentación con `///` a las 3 clases más importantes de tu proyecto

### Semana 4: Comunicación verbal
- [ ] Practica el framework PREP para tu próxima propuesta técnica
- [ ] En tu próximo standup, incluye **qué** estás haciendo, **por qué** importa y si tienes **blockers**
- [ ] Graba una explicación técnica de 3 minutos de algo que construiste y revísala críticamente

---

## Herramientas Recomendadas

| Herramienta | Uso |
|-------------|-----|