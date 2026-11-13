# negocio-no-chatgpt — ficha del negocio para la IA

[![Tu negocio en ChatGPT](guia/assets/banner-es.jpg)](https://inematds.github.io/negocio-no-chatgpt/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

Cuando alguien le pregunte a ChatGPT dónde comprar lo que vendes, tu negocio puede aparecer. La ficha del negocio para la IA deja todo listo en 10 minutos.

## Qué es

Desde el 10/11/2026, ChatGPT tiene, en fase de prueba, un registro oficial para negocios. Pero en Brasil, las tiendas físicas y los restaurantes todavía no pueden registrarse, y aun quienes pueden hacerlo solo aparecen si la IA entiende el negocio. **negocio-no-chatgpt** es un kit gratis para quienes tienen un negocio y quieren que la IA los encuentre: crea la **ficha del negocio para la IA** (el texto listo y el bloque de datos que va en el sitio) y califica tu sitio con una lista de lo que debes corregir. También incluye el paso a paso del registro, solo con lo que OpenAI confirmó. Solo necesitas una computadora con Python, que es gratis.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/negocio-no-chatgpt/guia/es/**

## La función y Brasil

**Businesses in ChatGPT** está en beta desde el 10/11/2026. En **Business Hub**, los negocios elegibles pueden reclamar y verificar su ficha, actualizar información y conectar un feed de productos. Los datos usados aquí provienen exclusivamente de [FONTES.md](FONTES.md) (en portugués).

**Brasil:** las tiendas físicas y los restaurantes solo pueden reclamar fichas existentes en Estados Unidos. Los negocios en línea pueden intentarlo; depende de las verificaciones de OpenAI. Business Agent todavía es solo para comercios electrónicos y servicios en línea elegibles en Estados Unidos. No se ha publicado una lista de países. Registrarse no garantiza ventas ni posicionamiento.

Kit público de INEMA, pequeño, en Python 3 y solo con la biblioteca estándar: sin pip ni cuenta de API.

## Instalación

Ten Python 3 instalado (Git es opcional: puedes [descargar el ZIP](https://github.com/inematds/negocio-no-chatgpt/archive/refs/heads/main.zip)). No hay dependencias que instalar. **En Windows, reemplaza `python3` por `py`** en todos los comandos.

```bash
git clone https://github.com/inematds/negocio-no-chatgpt
cd negocio-no-chatgpt
```

## Prepara la ficha

```bash
python3 ficha.py
```

Responde una pregunta a la vez. Para el tipo, puedes ingresar el número o el nombre (1 tienda física, 2 restaurante, 3 servicio local, 4 tienda en línea, 5 servicio en línea) y sinónimos comunes como “panadería”; si una respuesta no sirve (tipo, teléfono, correo electrónico o sitio web), se vuelve a preguntar sin perder el resto. El método **ficha del negocio para la IA** genera `ficha.md`, `jsonld.html`, `jsonld.json` y `checklist.md` en `minha-ficha/`. Revísalos antes de publicar. El script nunca usa la red.

Para usar un archivo con las mismas claves de las preguntas, copia y edita [respostas.json](exemplos/padaria/respostas.json). Los productos y servicios son una lista; las preguntas frecuentes son hasta cinco objetos con `pergunta` y `resposta`. Los nombres exactos de las claves están en el ejemplo. Solo son obligatorios `nome`, `o_que_vende`, `tipo` y al menos uno entre `cidade` y `site`. El teléfono, WhatsApp, correo electrónico y sitio web se validan cuando se completan.

```bash
python3 ficha.py --de exemplos/padaria/respostas.json --saida exemplos/padaria/minha-ficha
```

Salida real:

```text
ficha do negócio para a IA gerada em exemplos/padaria/minha-ficha/
Arquivos: ficha.md, jsonld.html, jsonld.json, checklist.md
```

Pega los textos de `ficha.md` en el sitio, en los perfiles y en los campos correspondientes de Business Hub, si cumples los requisitos. Pega `jsonld.html` en el `<head>` del sitio; `jsonld.json` contiene los mismos datos en JSON puro. Sigue `checklist.md` y el [paso a paso del registro](CADASTRO.md) (en portugués).

Horarios reconocidos: `seg-sex 9h-18h, sáb 9h-13h`, `ter 9h30-18h`, `dom 09:00-12:00`. Separa los períodos con coma o punto y coma. Si algún fragmento no se reconoce, se omite todo el campo `openingHours` y la lista de verificación lo indica; el texto original permanece en la ficha. No se adivinan los horarios.

## Revisa el sitio

```bash
python3 checar_site.py exemplos/sites/bom/index.html
python3 checar_site.py https://seu-site.com.br
python3 checar_site.py seu-site.html --robots caminho/robots.txt --llms caminho/llms.txt
python3 checar_site.py exemplos/sites/bom/index.html --json
```

Fragmento de la salida real del buen ejemplo:

```text
ficha do negócio para a IA — nota: 100/100

OK
- OAI-SearchBot liberado nesta página; sem meta noindex.
- JSON-LD válido com tipo de negócio.
- Título e descrição dentro dos tamanhos recomendados pelo kit.
- Contato e localização legíveis no texto da página.
- Texto visível: 198 palavras (mínimo do kit: 150).
- llms.txt presente: opcional, sem garantia de efeito.

CORRIGIR
- Nenhum item.
```

El verificador usa HTMLParser y lee HTML sin ejecutar JavaScript. Para un archivo local, busca `robots.txt` y `llms.txt` en la misma carpeta o usa las rutas indicadas. Para una URL, solo hace GET con urllib, con un tiempo de espera de 15 segundos por solicitud, hasta cinco redirecciones por recurso y lectura de un máximo de 2 MB por recurso. Busca los archivos auxiliares en el origen de la página final. User-Agent: `negocio-no-chatgpt-checador/1.0`. Los archivos que alcanzan el límite de lectura remota se rechazan para evitar un análisis truncado.

La puntuación de 0 a 100 es una heurística del kit: acceso 30, JSON-LD 20, título/descripción 15, contacto/ubicación 20, texto visible 10 y llms.txt opcional 5. Deben cumplirse juntos los criterios de cada grupo. Si no hay robots.txt, se permite el acceso; si falla la consulta, se informa como no verificado. GPTBot y ChatGPT-User son informativos y no restan puntos. Bloquear GPTBot (entrenamiento) no elimina el sitio de las búsquedas.

Para la ubicación, incluye en el texto visible la misma ciudad que figura en el JSON-LD, un código postal o un formato explícito como `Cidade: Joinville` o `Joinville/SC`. El verificador no reconoce automáticamente todas las ciudades. Reconoce tipos comunes de negocios enumerados al inicio del código; no descarga el catálogo de schema.org. No verifica CSS externo, la representación de JavaScript ni la autorización de IP en el servidor/CDN. No se ha confirmado que JSON-LD y llms.txt tengan efecto en el posicionamiento; llms.txt es opcional y no hay garantía de que tenga efecto.

El programa devuelve el código 0 cuando puede leer la página, incluso si la puntuación es baja, y el código 2 cuando no puede. Con `--json`, los resultados y los errores están en formato JSON. Todos los datos de los ejemplos son inventados; no uses sus datos de contacto como si fueran reales.

Esto facilita que la IA lea el sitio. No garantiza el posicionamiento: ChatGPT decide qué aparece.

## Pruebas sin red

```bash
python3 testes/run.py
```

Las pruebas bloquean las conexiones de red y cubren la generación, la validación, los horarios, el HTML, robots.txt, los límites de lectura y las redirecciones con respuestas simuladas.

Guía completa: https://inematds.github.io/negocio-no-chatgpt/guia/es/

## Kits complementarios

- [sitio que vende](https://inematds.github.io/site-que-vende/guia/)
- [atención de leads](https://inematds.github.io/atende-leads/guia/)

Licencia MIT, 2026 INEMA. Versión 1.0.0.

**gratis en inema.club, directamente en internet**
