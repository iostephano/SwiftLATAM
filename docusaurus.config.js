// @ts-check
const {themes} = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'SwiftLATAM',
  tagline: 'Aprende SwiftUI en español',
  favicon: 'img/favicon.ico',
  url: 'https://iostephano.github.io',
  baseUrl: '/SwiftLATAM/',
  organizationName: 'iostephano',
  projectName: 'SwiftLATAM',
  trailingSlash: false,
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'es',
    locales: ['es'],
  },

  presets: [
    [
      'classic',
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig: ({
    navbar: {
      title: 'SwiftLATAM',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Curso',
        },
        {
          href: 'https://github.com/iostephano/SwiftLATAM',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `SwiftLATAM © ${new Date().getFullYear()}`,
    },
    prism: {
      theme: themes.github,
      darkTheme: themes.dracula,
      additionalLanguages: ['swift'],
    },
  }),
};

module.exports = config;
```

Guarda el archivo (Cmd + S).

---

## PASO 4 — Crear tu primera lección real

En Terminal ejecuta:
```
rm -rf /Users/iostephano/SwiftLATAM/docs/*
```

Esto borra el contenido de ejemplo. Luego crea la estructura:
```
mkdir -p /Users/iostephano/SwiftLATAM/docs/fundamentos
```

Ahora crea el archivo de introducción:
```
cat > /Users/iostephano/SwiftLATAM/docs/fundamentos/introduccion.md << 'EOF'
---
sidebar_position: 1
title: Introducción a SwiftUI
---

# Introducción a SwiftUI

SwiftUI es el framework moderno de Apple para construir interfaces de usuario en iOS, macOS, watchOS y tvOS.

## ¿Qué es SwiftUI?

En lugar de describir **cómo** construir la interfaz paso a paso, describes **qué** debe mostrar, y SwiftUI se encarga del resto.

## Tu primera View

Todo en SwiftUI es una `View`. Un texto, una imagen, toda tu pantalla — todo es una View.
```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        Text("¡Hola, SwiftLATAM!")
            .font(.largeTitle)
            .foregroundStyle(.orange)
            .padding()
    }
}
```

## Ventajas frente a UIKit

- **Menos código** — lo que en UIKit son 50 líneas, en SwiftUI son 5
- **Previews en tiempo real** — Xcode muestra el resultado mientras escribes
- **Multi-plataforma** — el mismo código corre en iPhone, iPad y Mac

:::tip Consejo
Si empiezas hoy, SwiftUI es el camino correcto. Todo el ecosistema moderno de Apple apunta hacia aquí.
:::
EOF
```

Luego crea el índice del módulo:
```
cat > /Users/iostephano/SwiftLATAM/docs/fundamentos/_category_.json << 'EOF'
{
  "label": "Fundamentos",
  "position": 1,
  "collapsible": true,
  "collapsed": false
}
EOF
```

---

## PASO 5 — Verificar en local
```
cd /Users/iostephano/SwiftLATAM
npm start
```

Abre `localhost:3000` y verás SwiftLATAM con tu primera lección real.

---

## PASO 6 — Publicar en GitHub Pages

Cuando estés conforme, ejecuta en Terminal:
```
npm run build
```

Cuando termine:
```
GIT_USER=iostephano npm run deploy
