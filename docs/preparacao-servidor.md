# Preparação e homologação do servidor

Este guia complementa o [roteiro do evento](roteiro_evento_mansao_milionario.md). Não é um arquivo de configuração para importar no DayZ.

## 1. Decisões necessárias

Preencha estas informações antes de anunciar o evento:

| Decisão | O que registrar |
| --- | --- |
| Mapa e local | Mapa, versão, coordenadas da mansão e rota de extração. |
| Construção | Mod/estrutura escolhida, garagem utilizável, portas e espaço de circulação. |
| Veículo | Mod, versão, classname real, peças, consumo e sistema de chaves. |
| IA | Mod e dependências, facção hostil, patrulhas, loadouts e comportamento em interiores. |
| Infectado especial | Classe existente ou customizada, resistência, spawn e loot recuperável. |
| Acesso à garagem | Sistema de portas/cartões e mecanismo real de trancamento. |
| Economia | Mod de trader, moeda, itens de luxo, preços e venda do veículo. |
| Operação | Número de participantes, staff responsável, duração e reset do evento. |
| Regras PvE | Como registrar a posse e um prazo fixo de retorno: escolher 15 **ou** 20 minutos. |
| Divulgação | Data, horário, localização/dica e regras finais, sem placeholders. |

Registre também os IDs do Workshop, versões e dependências dos mods aprovados. Os nomes e imagens do repositório não comprovam disponibilidade, autoria ou compatibilidade.

## 2. As duas etapas de acesso

O fluxo esperado é:

```text
Líder da gangue → cartão da garagem → abertura da porta
Milionário infectado → chave vinculada → uso/extração do veículo
```

O cartão e a chave são dois objetivos de progressão, mas não necessariamente duas chaves da mesma porta. Se a porta também precisar exigir a chave do carro, isso requer uma integração adicional que deve ser implementada e testada. Não existe essa integração neste repositório.

- `CarKey` é um nome ilustrativo no conceito: use a classe de chave e o procedimento de pareamento do mod escolhido.
- O veículo deve estar vinculado à chave **antes** de o evento começar. Confirme o que esse sistema realmente bloqueia: portas, partida, condução ou apenas propriedade.
- Teste se o cartão e a chave podem ser recuperados dos corpos. Não presuma que qualquer infectado aceite inventário personalizado ou solte itens ao morrer.
- Um infectado de terno, com resistência elevada, pode exigir uma classe própria. Não presuma que seja possível vestir um infectado como um personagem comum.
- Defina uma recuperação supervisionada para perda/despawn de um item obrigatório; não entregue o prêmio livremente por causa de uma falha técnica.

## 3. Veículo e extração

- [ ] Confirmar que o carro cabe na garagem e sai pelo portão sem colisões.
- [ ] Conferir rodas, motor, radiador e lataria em boas condições.
- [ ] Retirar a bateria e a vela apenas se essas peças forem necessárias nesse veículo.
- [ ] Deixar combustível baixo e água insuficiente no radiador, conforme o desafio planejado.
- [ ] Disponibilizar bateria, vela, combustível e **água suficiente para completar o radiador**. Uma garrafa/cantil pode não bastar; teste a capacidade real.
- [ ] Validar a partida após a montagem e garantir que o motor não seja arruinado imediatamente por falta de água.
- [ ] Validar chave/fechaduras e impedimento de extração antes de cumprir os objetivos.
- [ ] Testar a rota até o Colecionador e a venda do classname correto do veículo.

## 4. Economia e balanceamento

Os intervalos do roteiro são sugestões, não preços implementados. Considerando todos os itens previstos na tabela, sem incluir loot extra dos guardas:

| Categoria | Quantidade | Valor unitário | Total possível |
| --- | --- | --- | --- |
| Tier 1 | 8–12 | 5.000–10.000 | 40.000–120.000 |
| Tier 2 | 4–6 | 20.000–35.000 | 80.000–210.000 |
| Tier 3 | 2 | 50.000–80.000 | 100.000–160.000 |
| **Itens de luxo** | **14–20** | — | **220.000–490.000** |
| Veículo | 1 | 300.000–500.000 | 300.000–500.000 |
| **Itens + venda do veículo** | — | — | **520.000–990.000** |

Escolha valores fixos e coerentes com a economia do servidor. O grupo pode coletar menos que o total planejado. Não anuncie um lucro garantido. Caso esses totais sejam altos demais, reduza quantidades/preços antes de disponibilizar a venda.

## 5. Homologação em ambiente de teste

- [ ] Carregar o mapa e os mods sem erros de dependência; verificar logs.
- [ ] Conferir navegação da IA em portas, corredores e escadas, sem bots presos nas paredes.
- [ ] Validar quantidades, dano e dificuldade com um grupo representativo.
- [ ] Executar as quatro fases do início ao fim, recuperando cartão, chave e loot.
- [ ] Testar falhas: grupo derrotado, cartão/chave perdidos, tentativa de sair sem chave e carro danificado.
- [ ] Testar a venda de cada item e do carro; confirmar que o veículo não é vendido normalmente pelo trader se for exclusivo.
- [ ] Se houver reforços finais, testar o gatilho e garantir que ele não se repita indefinidamente. O roteiro propõe esse recurso, mas não fornece código para ele.
- [ ] Conferir persistência e lifetime/despawn de corpos, peças, loot e veículo durante toda a sessão.
- [ ] Testar o reset: remover sobras, recriar inimigos e loot, refazer pareamento da chave e trancar a garagem.
- [ ] Revisar regras, posse, prazo de retorno e comunicação da staff.
- [ ] Confirmar as permissões de uso das mídias e substituir referências não autorizadas.

Após a homologação, registre as configurações reais em documentação específica ou em arquivos do sistema utilizado. Evite exemplos que pareçam configurações prontas sem conhecer o schema e a versão dos mods.
