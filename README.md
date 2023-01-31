# Corvus - Search ShareableAI Models

Corvus is a CLI tool that wraps the Searcher from [Jackdaw](https://github.com/shareableai/jackdaw). Designed for interactive and programmatic access to models saved via the ShareableAI toolkit.
## Usage

### Set API Key
```bash
corvus set api_key
```
Follow the interactive prompt - this helps avoid having the API Key visible within the terminal history.

### List Models

#### Local Models
```bash
corvus list --local
```

#### Remote Models
Requires an API Key to be set
```bash
corvus list --remote
```

#### Search
Searches for all models in the Jackdaw repo on the main branch.
```bash
corvus list --repo jackdaw --branch main
```

Search for all models on the main branch of any repo;
```bash
corvus list --branch main
```

Search for all models on feature branches;
```bash
corvus list --repo 'feat/%'
```

