---
sidebar_position: 1
title: Uikit Mastery
---

# UIKit Mastery: Dominio Completo del Framework Fundacional de iOS

## ¿Qué es UIKit y por qué dominarlo a fondo?

UIKit es el framework fundacional que Apple creó para construir interfaces de usuario en iOS. Aunque SwiftUI ha ganado popularidad desde 2019, **UIKit sigue siendo el pilar de la inmensa mayoría de aplicaciones en producción** a nivel mundial y, especialmente, en Latinoamérica.

Dominar UIKit no es simplemente conocer `UIViewController` y `UITableView`. Significa comprender el ciclo de vida de las vistas, el sistema de Auto Layout a nivel profundo, la arquitectura de responders, el rendering pipeline, las animaciones de Core Animation y cómo cada pieza interactúa con el sistema operativo subyacente.

## ¿Por qué es crítico para un developer iOS en LATAM?

### Realidad del mercado latinoamericano

1. **El 85-90% de los proyectos empresariales en la región usan UIKit.** Bancos como Banorte, Mercado Libre, Rappi, Nubank y prácticamente toda fintech relevante tiene bases de código en UIKit.
2. **Las ofertas remotas para empresas de EE.UU. y Europa exigen UIKit.** Si aspiras a salarios en dólares trabajando desde LATAM, el dominio de UIKit es un diferenciador clave en entrevistas técnicas.
3. **Migración progresiva.** Incluso los equipos que adoptan SwiftUI necesitan developers que entiendan UIKit para mantener, integrar y migrar código legacy.
4. **Soporte de versiones anteriores.** Muchas apps en LATAM aún soportan iOS 14 o 15, donde SwiftUI tiene limitaciones significativas.

## Los Pilares del Dominio de UIKit

### 1. Ciclo de Vida del View Controller

Comprender exactamente cuándo y por qué se ejecuta cada método es fundamental:

```swift
class ProfileViewController: UIViewController {

    // MARK: - Lifecycle

    override func loadView() {
        // Aquí creas la vista raíz manualmente (sin Storyboard)
        // Se llama UNA sola vez
        let customView = ProfileView()
        self.view = customView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        // Se llama UNA sola vez después de que la vista se cargó en memoria
        // Ideal para configuración inicial, bindings, llamadas de red
        setupNavigationBar()
        fetchUserProfile()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // Se llama CADA VEZ que la vista está a punto de aparecer
        // Ideal para actualizar datos que pudieron cambiar
        navigationController?.setNavigationBarHidden(false, animated: animated)
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        // La vista ya es visible. Ideal para iniciar animaciones o analytics
        trackScreenView(name: "profile")
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        // A punto de desaparecer. Cancelar timers, pausar video, etc.
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        // Ya desapareció. Liberar recursos pesados si es necesario
    }

    // MARK: - Memory Warning
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Liberar caches, imágenes no visibles, etc.
        imageCache.removeAll()
    }

    // MARK: - Private Methods

    private func setupNavigationBar() {
        title = "Mi Perfil"
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .edit,
            target: self,
            action: #selector(editProfile)
        )
    }

    private func fetchUserProfile() {
        // Llamada de red inicial
    }

    @objc private func editProfile() {
        let editVC = EditProfileViewController()
        navigationController?.pushViewController(editVC, animated: true)
    }

    private var imageCache: [String: UIImage] = [:]
}
```

> **Error común en entrevistas:** Confundir `viewDidLoad` con `viewWillAppear`. Si pones lógica de actualización en `viewDidLoad`, no se ejecutará cuando el usuario regrese con "back" desde otro view controller.

### 2. Auto Layout Programático: Dominio Absoluto

Los mejores equipos de iOS en LATAM trabajan **sin Storyboards**. Auto Layout programático te da control total, elimina conflictos en Git y mejora la legibilidad:

```swift
class CardView: UIView {

    // MARK: - UI Elements

    private let avatarImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.translatesAutoresizingMaskIntoConstraints = false
        imageView.contentMode = .scaleAspectFill
        imageView.clipsToBounds = true
        imageView.layer.cornerRadius = 30
        imageView.backgroundColor = .systemGray5
        return imageView
    }()

    private let nameLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.font = .systemFont(ofSize: 18, weight: .bold)
        label.textColor = .label
        label.numberOfLines = 1
        return label
    }()

    private let descriptionLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.font = .systemFont(ofSize: 14, weight: .regular)
        label.textColor = .secondaryLabel
        label.numberOfLines = 3
        return label
    }()

    private let actionButton: UIButton = {
        let button = UIButton(type: .system)
        button.translatesAutoresizingMaskIntoConstraints = false
        button.setTitle("Conectar", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 16, weight: .semibold)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 12
        return button
    }()

    // MARK: - Initialization

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
        setupConstraints()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    // MARK: - Setup

    private func setupUI() {
        backgroundColor = .systemBackground
        layer.cornerRadius = 16
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOpacity = 0.1
        layer.shadowOffset = CGSize(width: 0, height: 4)
        layer.shadowRadius = 12

        [avatarImageView, nameLabel, descriptionLabel, actionButton].forEach {
            addSubview($0)
        }
    }

    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Avatar
            avatarImageView.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            avatarImageView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            avatarImageView.widthAnchor.constraint(equalToConstant: 60),
            avatarImageView.heightAnchor.constraint(equalToConstant: 60),

            // Nombre
            nameLabel.topAnchor.constraint(equalTo: avatarImageView.topAnchor, constant: 4),
            nameLabel.leadingAnchor.constraint(equalTo: avatarImageView.trailingAnchor, constant: 12),
            nameLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),

            // Descripción
            descriptionLabel.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 4),
            descriptionLabel.leadingAnchor.constraint(equalTo: nameLabel.leadingAnchor),
            descriptionLabel.trailingAnchor.constraint(equalTo: nameLabel.trailingAnchor),

            // Botón
            actionButton.topAnchor.constraint(greaterThanOrEqualTo: descriptionLabel.bottomAnchor, constant: 16),
            actionButton.topAnchor.constraint(greaterThanOrEqualTo: avatarImageView.bottomAnchor, constant: 16),
            actionButton.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            actionButton.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            actionButton.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16),
            actionButton.heightAnchor.constraint(equalToConstant: 48),
        ])
    }

    // MARK: - Configuration

    func configure(name: String, description: String, avatarImage: UIImage?) {
        nameLabel.text = name
        descriptionLabel.text = description
        avatarImageView.image = avatarImage
    }
}
```

### 3. UICollectionView con Compositional Layout y Diffable Data Sources

Este es el **estándar moderno de UIKit** y lo que preguntan en entrevistas para empresas top:

```swift
class FeedViewController: UIViewController {

    // MARK: - Types

    enum Section: Int, CaseIterable {
        case stories
        case posts
        case suggestions
    }

    struct Item: Hashable {
        let id: UUID
        let title: String
        let section: Section

        func hash(into hasher: inout Hasher) {
            hasher.combine(id)
        }
    }

    // MARK: - Properties

    private var collectionView: UICollectionView!
    private var dataSource: UICollectionViewDiffableDataSource<Section, Item>!

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupCollectionView()
        configureDataSource()
        applyInitialSnapshot()
    }

    // MARK: - Collection View Setup

    private func setupCollectionView() {
        collectionView = UICollectionView(
            frame: view.bounds,
            collectionViewLayout: createLayout()
        )
        collectionView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        collectionView.backgroundColor = .systemGroupedBackground
        collectionView.delegate = self

        // Registrar celdas
        collectionView.register(StoryCell.self, forCellWithReuseIdentifier: StoryCell.reuseID)
        collectionView.register(PostCell.self, forCellWithReuseIdentifier: PostCell.reuseID)
        collectionView.register(SuggestionCell.self, forCellWithReuseIdentifier: SuggestionCell.reuseID)

        view.addSubview(collectionView)
    }

    // MARK: - Compositional Layout

    private func createLayout() -> UICollectionViewCompositionalLayout {
        return UICollectionViewCompositionalLayout { [weak self] sectionIndex, environment in
            guard let section = Section(rawValue: sectionIndex) else { return nil }

            switch section {
            case .stories:
                return self?.createStoriesSection()
            case .posts:
                return self?.createPostsSection(environment: environment)
            case .suggestions:
                return self?.createSuggestionsSection()
            }
        }
    }

    private func createStoriesSection() -> NSCollectionLayoutSection {
        // Item
        let itemSize = NSCollectionLayoutSize(
            widthDimension: .absolute(80),
            heightDimension: .absolute(100)
        )
        let item = NSCollectionLayoutItem(layoutSize: itemSize)
        item.contentInsets = NSDirectionalEdgeInsets(top: 0, leading: 4, bottom: 0, trailing: 4)

        // Grupo horizontal que scrollea
        let groupSize = NSCollectionLayoutSize(
            widthDimension: .absolute(80),
            heightDimension: .absolute(100)
        )
        let group = NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, subitems: [item])

        // Sección con scroll horizontal
        let section = NSCollectionLayoutSection(group: group)
        section.orthogonalScrollingBehavior = .continuous
        section.contentInsets = NSDirectionalEdgeInsets(top: 8, leading: 12, bottom: 8, trailing: 12)

        return section
    }

    private func createPostsSection(environment: NSCollectionLayoutEnvironment) -> NSCollectionLayoutSection {
        let itemSize = NSCollectionLayoutSize(
            widthDimension: .fractionalWidth(1.0),
            heightDimension: .estimated(400)
        )
        let item = NSCollectionLayoutItem(layoutSize: itemSize)

        let groupSize = NSCollectionLayoutSize(
            widthDimension: .fractionalWidth(1.0),
            heightDimension: .estimated(400)
        )
        let group = NSCollectionLayoutGroup.vertical(layoutSize: groupSize, subitems: [item])

        let section = NSCollectionLayoutSection(group: group)
        section.interGroupSpacing = 12
        section.contentInsets = NSDirectionalEdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16)

        return section
    }

    private func createSuggestionsSection() -> NSCollectionLayoutSection {
        let itemSize = NSCollectionLayoutSize(
            widthDimension: .fractionalWidth(1.0),
            heightDimension: .fractionalHeight(1.0)
        )
        let item = NSCollectionLayoutItem(layoutSize: itemSize)

        let groupSize = NSCollectionLayoutSize(
            widthDimension: .absolute(200),
            heightDimension: .absolute(250)
        )
        let group = NSCollectionLayoutGroup.horizontal(layoutSize: groupSize, subitems: [item])

        let section = NSCollectionLayoutSection(group: group)
        section.orthogonalScrollingBehavior = .groupPagingCentered
        section.interGroupSpacing = 12
        section.contentInsets = NSDirectionalEdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16)

        return section
    }

    // MARK: - Diffable Data Source

    private func configureDataSource() {
        dataSource = UICollectionViewDiffableDataSource<Section, Item>(
            collectionView: collectionView
        ) { collectionView, indexPath, item in

            switch item.section {
            case .stories:
                let cell = collectionView.dequeueReusableCell(
                    withReuseIdentifier: StoryCell.reuseID,
                    for: indexPath
                ) as! StoryCell
                cell.configure(with: item.title)
                return cell

            case .posts:
                let cell = collectionView.dequeueReusableCell(
                    withReuseIdentifier: PostCell.reuseID,
                    for: indexPath
                ) as! PostCell
                cell.configure(with: item.title)
                return cell

            case .suggestions:
                let cell = collectionView.dequeueReusableCell(
                    withReuseIdentifier: SuggestionCell.reuseID,
                    for: indexPath
                ) as! SuggestionCell
                cell.configure(with: item.title)
                return cell
            }
        }
    }

    private func applyInitialSnapshot() {
        var