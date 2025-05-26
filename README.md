# Calculate image costs

Each image you include in a request to Claude counts towards your token usage. To calculate the approximate cost, multiply the approximate number of image tokens by the per-token price of the model you’re using.

If your image does not need to be resized, you can estimate the number of tokens used through this algorithm: tokens = (width px \* height px)/750

Here are examples of approximate tokenization and costs for different image sizes within our API’s size constraints based on Claude 3.7 Sonnet per-token price of $3 per million input tokens:

Image size # of Tokens Cost / image Cost / 1K images
200x200 px(0.04 megapixels) ~54 ~$0.00016 ~$0.16
1000x1000 px(1 megapixel) ~1334 ~$0.004 ~$4.00
1092x1092 px(1.19 megapixels) ~1590 ~$0.0048 ~$4.80

Pegar o livro e transformar em embedding

## Etapas

- 1. Realizar o upload dos livros para o S3.

### 1. Realizar o upload dos livros para o S3

- Duranto o upload dos livros, se faz necessário identicar as edições do mesmo livro, e salvar na mesma pasta, talvez com esse padrao, `livro/edicao`.
- Salvar cada pagina do livro em um arquivo separado, com o nome da pagina, e o nome do livro, para facilitar a busca depois.

Estrutura de pastas:

```text
livros
├── livro1
│   ├── edicao1
│   ├──── pagina1.txt
│   ├──── pagina2.txt
│   ├── edicao2
│   ├──── pagina1.txt
│   ├──── pagina2.txt
├── livro2
│   ├── edicao1
│   ├──── pagina1.txt
│   ├──── pagina2.txt
│   ├── edicao2
│   ├──── pagina1.txt
│   ├──── pagina2.txt
```

### Realizando a pesquisa por leis contidas em uma pagina

Utilizar a api do senado para procurar por uma leia descrita na pagina do livro, fazer uma pesquisa pelo processo dela.

```http
GET /dadosabertos/processo HTTP/1.1
Host: https://legis.senado.leg.br/dadosabertos/processo?v=1
```

- A resposta anterior retorna alguns campos e com `id` do processo, é possivel buscar mais informações sobre o mesmo.

```http
GET /dadosabertos/processo/{id} HTTP/1.1
Host: https://legis.senado.leg.br/dadosabertos/processo/{id}?v=1
```

**Obs:** No momento de pesquisa da api o endpoint `/dadosabertos/processo/{id}` não está retornando os dados, mas o endpoint `/dadosabertos/processo` está retornando os dados.

## Observações dos arquivos

- Os livros tem o nome completo deles as vezes.
- Talvez não tenha o nome do autor.

## Ideias

- Para a curadoria dos livros implementar um interface google docs like, onde o usuario pode editar o livro, e adicionar as leis que ele encontrar.
- O vector seria complementado com as paginas geradas com a IA e pelas alterações feitas pelo usuario. Ex. "Segundo a lei 1234/2023, o artigo 1º de 1985 adulterio, era crime. Mas a lei 1234/2023 revogou o artigo 1º de 1985, e o crime de adulterio não existe mais."
- Durante o processo de ocr realizar a extração de ["titulo_livro", "autor", "editora", "Ano de publicação", "ISBN", "paginas", "edição", "volume", "Idioma"] e salvar no banco de dados, para facilitar a busca depois.
