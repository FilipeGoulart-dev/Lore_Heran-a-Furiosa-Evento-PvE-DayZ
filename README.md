# Herança Furiosa — Evento PvE para DayZ

**A Mansão do Milionário e o Tesouro sobre Rodas.** Um conceito de evento com combate contra IA, exploração, loot de luxo e extração de um veículo temático.

> **Estado do projeto:** planejamento e referências visuais. Este repositório **não é um mod instalável** e não contém configurações prontas de missão, bots, trader, portas ou veículos. A implementação depende do mapa e dos mods escolhidos pelo administrador.

## Por onde começar

| Material | Conteúdo |
| --- | --- |
| [Página inicial](index.html) | Apresentação do evento criada pelo responsável do projeto (arquivo autossuficiente, com mídias incorporadas). |
| [Roteiro do evento](docs/roteiro_evento_mansao_milionario.md) | Lore, quatro fases, inimigos, economia, regras e textos de divulgação. |
| [Preparação do servidor](docs/preparacao-servidor.md) | Decisões técnicas, cuidados e checklist de homologação. |
| [Catálogo de mídias](docs/catalogo-midia.md) | Todos os arquivos de imagem e áudio, agrupados por categoria. |
| [Relatório de verificação](docs/auditoria.md) | Problemas encontrados, ajustes realizados e pendências. |

## Estrutura

```text
.
├── index.html                    # Apresentação original do evento (HTML autossuficiente)
├── assets/
│   ├── images/
│   │   ├── vehicles/              # Charger, Skyline, RX-7 e Silvia
│   │   ├── locations/             # Mansões, construções e mapa
│   │   ├── mods/                  # IA, colecionáveis, mineração e dinheiro
│   │   └── references/            # Captura da apresentação anterior
│   └── audio/                    # Referência de áudio existente
├── docs/                         # Roteiro, guias e inventário das mídias
├── scripts/check_repository.py   # Verificação local e atualização do catálogo
├── tests/                        # Testes do verificador
└── .github/workflows/verify.yml   # Verificações no GitHub Actions
```

Os nomes originais das mídias foram mantidos. O [inventário JSON](docs/inventario-midia.json) registra o caminho antigo, o caminho atual, o tamanho e o SHA-256 de cada arquivo. As duas imagens idênticas foram preservadas e identificadas no catálogo.

## Abrir a apresentação

A página funciona diretamente ao abrir `index.html` em um navegador. Para servir o repositório localmente ou pela prévia do workspace, use **Python 3.10 ou superior**:

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

Em uma máquina local, abra `http://localhost:8000`. No workspace, use o endereço de prévia fornecido pela plataforma.

O `index.html` é a **apresentação original do evento**, mantida byte a byte como foi enviada pelo responsável do projeto. Ela é autossuficiente: as imagens e a música estão incorporadas no próprio arquivo, que também traz seus estilos e scripts embutidos e links para as páginas do Workshop no Steam. Por isso o arquivo tem cerca de 10 MB e deve ser editado apenas pelo responsável do projeto. Os documentos em `docs/` são arquivos Markdown: leia-os pelo GitHub ou em um editor; um servidor estático pode exibi-los como texto ou oferecer o download.

Para GitHub Pages, após revisar as permissões das mídias, configure a publicação da raiz da branch desejada nas configurações do repositório. O arquivo `.nojekyll` permite servir os arquivos sem processamento pelo Jekyll. Nenhuma publicação foi ativada por esta organização.

## Verificar o repositório

Não é necessário instalar pacotes. Com Python 3.10+:

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
```

O verificador confere arquivos e fragmentos HTML/Markdown referenciados localmente, assinaturas de formato das mídias, tamanhos, hashes e sincronização do catálogo. Duplicatas são avisos, não falhas. Ele não consulta links externos, não decodifica integralmente as mídias e não testa um servidor DayZ. Veja o escopo da auditoria no relatório.

## Manter a organização

1. Edite o roteiro canônico em `docs/roteiro_evento_mansao_milionario.md`. O `index.html` é a apresentação autoral do responsável do projeto: altere-o somente a pedido dele.
2. Coloque novas imagens na categoria adequada e áudio em `assets/audio/`. Use nomes descritivos, de preferência em minúsculas e sem espaços.
3. Registre autoria, origem e autorização de uso no relatório antes de publicar novas mídias.
4. **Somente após uma alteração intencional e revisada de mídia**, atualize o inventário e o catálogo:

   ```bash
   python3 scripts/check_repository.py --update-inventory
   ```

   Esse comando aceita os bytes atuais como nova referência. Não o use para ocultar uma alteração inesperada ou corrupção; revise o diff do inventário. Para novos arquivos, `original_path` fica `null`; ao renomear um arquivo já inventariado, atualize seu campo `path` antes de executar o comando para preservar o histórico de origem.

5. Execute novamente as verificações e os testes. Não edite manualmente `docs/catalogo-midia.md`, pois ele é gerado a partir do inventário.

## Limites e permissões

- Os veículos, mansões e mods apresentados são **referências**, não dependências instaladas ou uma lista de compatibilidade confirmada.
- Classnames, IDs do Workshop, versões, posições, preços e integrações precisam ser definidos e testados no servidor.
- Não há licença declarada no material original. Imagens, marcas e áudio podem pertencer a terceiros; a organização do repositório não concede direitos de redistribuição. Confirme as permissões antes de publicar ou usar as mídias no servidor.
