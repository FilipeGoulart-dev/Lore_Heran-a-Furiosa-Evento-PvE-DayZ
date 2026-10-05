# Relatório de verificação e organização

**Data:** 5 de outubro de 2026.

**Referência inicial:** commit `1324f3aa58d2545eb2d1802b78ec8938cbb589de`.

## Diagnóstico inicial

- 43 arquivos na raiz: um roteiro Markdown, um `index.html` sem conteúdo (apenas uma quebra de linha), 40 imagens e um MP3.
- Ausência de README, separação por diretórios, instruções de uso e verificações automatizadas.
- Nenhum código de mod, configuração de servidor ou lista confirmada de dependências. O material representa um conceito de evento.
- Duas imagens com os mesmos bytes, mas nomes de veículos diferentes.
- Algumas miniaturas pequenas e referências cujo conteúdo não corresponde claramente ao nome do arquivo.
- Inconsistências no acesso à garagem e na estimativa de receita dos itens de luxo.

## Ajustes realizados

1. Roteiro movido para `docs/`, mantendo a história, as fases e os textos de divulgação.
2. Mídias separadas em veículos, locais, mods, referências e áudio. **Nenhuma mídia original foi removida, recomprimida ou modificada.**
3. Criados README, guia de preparação e catálogo de todos os arquivos.
4. Criada uma página estática em `index.html`, substituindo a página vazia. Ela usa imagens locais e não incorpora streaming nem o MP3 de origem desconhecida.
5. Registrados caminhos originais, tamanhos e SHA-256 no [inventário](inventario-midia.json).
6. Adicionados verificador sem dependências, testes unitários e workflow de verificação no GitHub Actions.
7. No roteiro, esclarecido que o cartão abre a garagem e a chave permite usar o carro conforme o mod escolhido; uma exigência conjunta na porta não é presumida.
8. Corrigida a estimativa de aproximadamente 150 mil moedas: as quantidades e preços sugeridos somam **220 mil a 490 mil** em itens de luxo. São valores teóricos, não ganhos garantidos.
9. Ajustado o checklist para exigir água suficiente para o radiador e a classe de chave real do mod, em vez de presumir uma garrafa ou uma classe universal.

## Integridade das mídias

Na auditoria inicial:

- As **40 imagens** (35 JPEG e 5 PNG) foram verificadas e decodificadas com Pillow, sem erro; os formatos correspondem às extensões.
- O **MP3** foi decodificado integralmente com FFmpeg, sem erro: aproximadamente **3 min 53 s**, 44,1 kHz, estéreo. Isso não identifica sua autoria ou licença.
- Os hashes das 41 mídias reorganizadas correspondem aos bytes do commit de referência.

O verificador do repositório usa apenas a biblioteca padrão do Python. Nas execuções recorrentes ele verifica assinaturas de formato, tamanho, SHA-256, cobertura do inventário, catálogo e referências locais. A decodificação completa descrita acima foi uma checagem pontual; não é feita pelo workflow. Links externos e execução no DayZ não foram testados.

### Duplicata preservada

Estes dois arquivos são idênticos (5.082 bytes cada):

- [Prévia nomeada como RX-7](../assets/images/vehicles/dayz-mazda-rx-7-fd-mod-car-2.jpg)
- [Prévia nomeada como Silvia S15](../assets/images/vehicles/dayz-nissan-silvia-s15-car-mod-dayz-2.jpg)

Ambos mostram a mesma miniatura de interior e não comprovam qual veículo está representado. Foram mantidos para não eliminar material sem decisão do responsável. O verificador apresenta um aviso, sem falhar por essa duplicata conhecida.

### Referências a revisar

- [Arquivo nomeado como mansão SSM](../assets/images/locations/dayz-ssm-mansion-mod-j-12-dayz-mansion-s-2.jpg): a imagem mostra uma divulgação de *Expansion Missions*, não uma vista da mansão. Não usá-la como confirmação do modelo de construção.
- Existem miniaturas de 140–148 pixels de largura: adequadas apenas como referências pequenas, não para banners ou identificação confiável de mods.
- `rx7_han_concept.jpg` e `rx7_han_concept.png` mostram o mesmo conceito visual em arquivos distintos. Não são duplicatas binárias; ambos foram preservados.
- A captura em `assets/images/references/` documenta um player incorporado indisponível na apresentação anterior. Não há HTML original funcional para recuperar a integração ou confirmar a fonte da música.

Consulte o [catálogo](catalogo-midia.md) para abrir cada arquivo. As categorias se baseiam nos nomes e temas do material existente, não em uma validação de autoria ou de compatibilidade.

## Verificações finais locais

- Verificador de referências, catálogo e integridade das 41 mídias: aprovado, com um aviso para o par de arquivos idênticos preservado.
- Comparação direta de cada mídia com o arquivo original no Git: 41 de 41 com bytes idênticos.
- Suite unitária do verificador: 20 testes aprovados.
- Página verificada no Chromium em larguras de 320, 390, 768, 1.024 e 1.440 pixels, sem overflow horizontal.
- Imagens, CSS e destinos dos links da página respondem por HTTP sem erro; navegação por âncoras e link de salto pelo teclado funcionam.
- Abertura direta do HTML com JavaScript desativado e carregamento sob um prefixo de projeto (simulação de GitHub Pages): aprovados.
- Checagem automática do axe-core para regras WCAG A/AA no desktop: sem violações apontadas. Isso não substitui uma auditoria manual completa de acessibilidade.

As ferramentas de navegador e decodificação usadas pontualmente não foram adicionadas como dependências do projeto. As verificações descritas acima foram realizadas localmente; os resultados do workflow devem ser consultados no GitHub. Não houve publicação do site nem execução do evento em um servidor DayZ.

## Pendências do responsável pelo servidor

- [ ] Definir mapa, coordenadas e construção final.
- [ ] Confirmar mods, IDs do Workshop, versões, dependências e direitos de uso.
- [ ] Definir classnames reais de veículos, itens, portas, cartões, chaves, IA e infectados.
- [ ] Implementar e testar spawn, patrulhas, loot, acesso, venda e reset.
- [ ] Escolher regras e preços finais; preencher os placeholders de divulgação.
- [ ] Registrar autoria/origem e permissões das imagens e do áudio antes de publicação ou redistribuição. O material original não declara licença; nenhuma licença foi atribuída automaticamente.
- [ ] Decidir se as miniaturas equivocadas ou duplicadas devem ser substituídas ou removidas numa revisão futura.

O [guia de preparação](preparacao-servidor.md) detalha os critérios de homologação. A organização não implica que o evento já esteja pronto para executar em um servidor DayZ.
