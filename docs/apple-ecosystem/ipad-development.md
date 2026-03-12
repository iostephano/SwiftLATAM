---
sidebar_position: 1
title: Ipad Development
---

# Desarrollo para iPad: Guía Completa

## ¿Qué es el desarrollo para iPad?

El desarrollo para iPad va mucho más allá de simplemente "escalar" una aplicación de iPhone a una pantalla más grande. Se trata de **diseñar y construir experiencias que aprovechen al máximo las capacidades únicas del iPad**: su pantalla amplia, el soporte para multitarea (Split View, Slide Over), el Apple Pencil, el trackpad/mouse, los atajos de teclado y las capacidades de arrastrar y soltar (Drag & Drop).

Apple ha posicionado al iPad como un dispositivo de productividad real. Desde iPadOS 13, el sistema operativo tiene su propia identidad separada de iOS, lo que significa que como desarrolladores tenemos APIs y paradigmas específicos que debemos dominar.

## ¿Por qué es importante para un desarrollador iOS en LATAM?

En Latinoamérica, el desarrollo para iPad representa una **oportunidad competitiva enorme** por varias razones:

- **Mercado empresarial en crecimiento**: Empresas en sectores como educación, salud, retail, logística y manufactura adoptan iPads como herramientas de trabajo. Aplicaciones de punto de venta (POS), sistemas de inventario y herramientas educativas tienen alta demanda en la región.
- **Diferenciación profesional**: La mayoría de los desarrolladores iOS en LATAM se enfocan exclusivamente en iPhone. Dominar iPad te posiciona como un profesional más completo y valioso para clientes internacionales.
- **Freelance y consultoría internacional**: Muchas empresas en EE.UU. y Europa buscan desarrolladores que puedan crear experiencias iPad de calidad. Desde LATAM, puedes ofrecer estos servicios a precios competitivos.
- **Catalyst y convergencia**: Con Mac Catalyst y Apple Silicon, una app iPad bien diseñada puede llegar también a macOS, multiplicando tu alcance.

---

## Conceptos Fundamentales

### 1. Layouts Adaptativos con Size Classes

El iPad puede presentar tu aplicación en múltiples tamaños de ventana. Las **Size Classes** son el mecanismo fundamental para adaptar tu interfaz.

| Configuración | Horizontal | Vertical |
|---|---|---|
| iPad pantalla completa | Regular | Regular |
| iPad Split View (2/3) | Regular | Regular |
| iPad Split View (1/2) | Compact | Regular |
| iPad Slide Over | Compact | Regular |
| iPhone | Compact | Regular |

```swift
import UIKit

class AdaptiveViewController: UIViewController {

    private let contentStackView: UIStackView = {
        let stack = UIStackView()
        stack.translatesAutoresizingMaskIntoConstraints = false
        stack.spacing = 16
        return stack
    }()

    private let sidebarView = SidebarView()
    private let detailView = DetailView()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        adaptLayout(for: traitCollection)
    }

    private func setupUI() {
        view.addSubview(contentStackView)
        contentStackView.addArrangedSubview(sidebarView)
        contentStackView.addArrangedSubview(detailView)

        NSLayoutConstraint.activate([
            contentStackView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            contentStackView.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor),
            contentStackView.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor),
            contentStackView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor)
        ])
    }

    override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
        super.traitCollectionDidChange(previousTraitCollection)

        if traitCollection.horizontalSizeClass != previousTraitCollection?.horizontalSizeClass {
            adaptLayout(for: traitCollection)
        }
    }

    private func adaptLayout(for traitCollection: UITraitCollection) {
        switch traitCollection.horizontalSizeClass {
        case .regular:
            // iPad pantalla completa o Split View amplio
            contentStackView.axis = .horizontal
            sidebarView.isHidden = false
            sidebarView.widthAnchor.constraint(equalToConstant: 320).isActive = true
        case .compact:
            // iPad Slide Over o Split View reducido
            contentStackView.axis = .vertical
            sidebarView.isHidden = true
        @unknown default:
            break
        }
    }
}
```

### 2. UISplitViewController: El Patrón de Navegación del iPad

El `UISplitViewController` es **el componente de navegación más importante** en iPad. Permite crear interfaces de columna múltiple que se adaptan automáticamente.

```swift
import UIKit

class MainSplitViewController: UISplitViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        // Configuración de tres columnas (iPadOS 14+)
        self.preferredDisplayMode = .twoBesideSecondary
        self.preferredSplitBehavior = .tile

        // Columna primaria (sidebar)
        let sidebar = SidebarViewController()
        setViewController(sidebar, for: .primary)

        // Columna suplementaria
        let supplementary = CategoryListViewController()
        setViewController(supplementary, for: .supplementary)

        // Columna secundaria (detalle)
        let detail = DetailViewController()
        let detailNav = UINavigationController(rootViewController: detail)
        setViewController(detailNav, for: .secondary)

        // Vista compacta (cuando el espacio es reducido)
        let compactTab = UITabBarController()
        setViewController(compactTab, for: .compact)
    }
}
```

### 3. Sidebar con UICollectionView (Estilo iPadOS)

Desde iPadOS 14, Apple introdujo el estilo de **sidebar** nativo que ves en apps como Archivos, Notas y Mail:

```swift
import UIKit

class SidebarViewController: UIViewController {

    enum SidebarItem: String, CaseIterable {
        case inbox = "Bandeja de entrada"
        case sent = "Enviados"
        case drafts = "Borradores"
        case trash = "Papelera"

        var icon: String {
            switch self {
            case .inbox: return "tray.fill"
            case .sent: return "paperplane.fill"
            case .drafts: return "doc.fill"
            case .trash: return "trash.fill"
            }
        }
    }

    private var collectionView: UICollectionView!
    private var dataSource: UICollectionViewDiffableDataSource<Int, SidebarItem>!

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Correo"
        navigationController?.navigationBar.prefersLargeTitles = true
        configureCollectionView()
        configureDataSource()
        applySnapshot()
    }

    private func configureCollectionView() {
        let layout = UICollectionViewCompositionalLayout.list(
            using: .init(appearance: .sidebar)
        )
        collectionView = UICollectionView(frame: view.bounds, collectionViewLayout: layout)
        collectionView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        collectionView.delegate = self
        view.addSubview(collectionView)
    }

    private func configureDataSource() {
        let cellRegistration = UICollectionView.CellRegistration<UICollectionViewListCell, SidebarItem> {
            cell, indexPath, item in

            var content = cell.defaultContentConfiguration()
            content.text = item.rawValue
            content.image = UIImage(systemName: item.icon)
            cell.contentConfiguration = content
        }

        dataSource = UICollectionViewDiffableDataSource<Int, SidebarItem>(
            collectionView: collectionView
        ) { collectionView, indexPath, item in
            collectionView.dequeueConfiguredReusableCell(
                using: cellRegistration, for: indexPath, item: item
            )
        }
    }

    private func applySnapshot() {
        var snapshot = NSDiffableDataSourceSnapshot<Int, SidebarItem>()
        snapshot.appendSections([0])
        snapshot.appendItems(SidebarItem.allCases, toSection: 0)
        dataSource.apply(snapshot, animatingDifferences: false)
    }
}

extension SidebarViewController: UICollectionViewDelegate {
    func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        guard let item = dataSource.itemIdentifier(for: indexPath) else { return }

        let detail = DetailViewController()
        detail.title = item.rawValue

        splitViewController?.setViewController(
            UINavigationController(rootViewController: detail),
            for: .secondary
        )
    }
}
```

### 4. Soporte para Drag & Drop

Una de las funcionalidades más poderosas del iPad es **arrastrar y soltar** contenido entre aplicaciones:

```swift
import UIKit

class DragDropViewController: UIViewController {

    private let imageView: UIImageView = {
        let iv = UIImageView()
        iv.contentMode = .scaleAspectFit
        iv.backgroundColor = .secondarySystemBackground
        iv.isUserInteractionEnabled = true
        iv.translatesAutoresizingMaskIntoConstraints = false
        iv.layer.cornerRadius = 12
        iv.clipsToBounds = true
        return iv
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupImageView()
        configureDragAndDrop()
    }

    private func setupImageView() {
        view.addSubview(imageView)
        NSLayoutConstraint.activate([
            imageView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            imageView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            imageView.widthAnchor.constraint(equalToConstant: 300),
            imageView.heightAnchor.constraint(equalToConstant: 300)
        ])
    }

    private func configureDragAndDrop() {
        // Permitir arrastrar la imagen desde nuestra app
        let dragInteraction = UIDragInteraction(delegate: self)
        imageView.addInteraction(dragInteraction)

        // Permitir soltar imágenes en nuestra app
        let dropInteraction = UIDropInteraction(delegate: self)
        imageView.addInteraction(dropInteraction)
    }
}

// MARK: - Drag
extension DragDropViewController: UIDragInteractionDelegate {
    func dragInteraction(
        _ interaction: UIDragInteraction,
        itemsForBeginning session: UIDragSession
    ) -> [UIDragItem] {
        guard let image = imageView.image else { return [] }
        let provider = NSItemProvider(object: image)
        let dragItem = UIDragItem(itemProvider: provider)
        dragItem.localObject = image
        return [dragItem]
    }
}

// MARK: - Drop
extension DragDropViewController: UIDropInteractionDelegate {
    func dropInteraction(
        _ interaction: UIDropInteraction,
        canHandle session: UIDropSession
    ) -> Bool {
        session.canLoadObjects(ofClass: UIImage.self)
    }

    func dropInteraction(
        _ interaction: UIDropInteraction,
        sessionDidUpdate session: UIDropSession
    ) -> UIDropProposal {
        UIDropProposal(operation: .copy)
    }

    func dropInteraction(
        _ interaction: UIDropInteraction,
        performDrop session: UIDropSession
    ) {
        session.loadObjects(ofClass: UIImage.self) { [weak self] items in
            guard let image = items.first as? UIImage else { return }
            DispatchQueue.main.async {
                self?.imageView.image = image
            }
        }
    }
}
```

### 5. Soporte para Apple Pencil

El Apple Pencil abre posibilidades para apps de dibujo, anotación y firma digital:

```swift
import UIKit
import PencilKit

class DrawingViewController: UIViewController {

    private let canvasView: PKCanvasView = {
        let canvas = PKCanvasView()
        canvas.translatesAutoresizingMaskIntoConstraints = false
        canvas.drawingPolicy = .anyInput // Permite dibujar con dedo y Pencil
        canvas.tool = PKInkingTool(.pen, color: .label, width: 5)
        canvas.backgroundColor = .systemBackground
        return canvas
    }()

    private let toolPicker = PKToolPicker()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupCanvas()
        setupToolbar()
    }

    private func setupCanvas() {
        view.addSubview(canvasView)
        canvasView.delegate = self

        NSLayoutConstraint.activate([
            canvasView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            canvasView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            canvasView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            canvasView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }

    private func setupToolbar() {
        toolPicker.setVisible(true, forFirstResponder: canvasView)
        toolPicker.addObserver(canvasView)
        canvasView.becomeFirstResponder()
    }

    private func setupNavigationActions() {
        navigationItem.rightBarButtonItems = [
            UIBarButtonItem(
                title: "Limpiar",
                style: .plain,
                target: self,
                action: #selector(clearCanvas)
            ),
            UIBarButtonItem(
                title: "Exportar",
                style: .done,
                target: self,
                action: #selector(exportDrawing)
            )
        ]
    }

    @objc private func clearCanvas() {
        canvasView.drawing = PKDrawing()
    }

    @objc private func exportDrawing() {
        let bounds = canvasView.drawing.bounds
        let image = canvasView.drawing.image(from: bounds, scale: UIScreen.main.scale)

        let activityVC = UIActivityViewController(
            activityItems: [image],
            applicationActivities: nil
        )

        // IMPORTANTE: En iPad, UIActivityViewController requiere popover
        activityVC.popoverPresentationController?.barButtonItem =
            navigationItem.rightBarButtonItems?.last

        present(activityVC, animated: true)
    }
}

extension DrawingViewController: PKCanvasViewDelegate {
    func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
        // Guardar automáticamente o actualizar estado
        print("El dibujo cambió. Total de trazos: \(canvasView.drawing.strokes.count)")
    }
}
```

### 6. Atajos de Teclado

Los usuarios de iPad con teclado externo esperan poder usar atajos. Esto es **fundamental para apps de productividad**:

```swift
import UIKit

class ProductivityViewController: UIViewController {

    // MARK: - Atajos de teclado
    override var keyCommands: [UIKeyCommand]? {
        return [
            UIKeyCommand(
                title: "Nuevo documento",
                action: #selector(createNewDocument),
                input: "N",
                modifierFlags: .command
            ),
            UIKeyCommand(
                title: "Guardar",
                action: #selector(saveDocument),
                input: "S",
                modifierFlags: .command
            ),
            UIKey