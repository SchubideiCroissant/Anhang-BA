## Simulation - Tool
### Installation
- `cd /typescript`

- create Python-Environment `python -m venv venv311`
- run environment ` .\venv311\Scripts\activate`

**Requirements**:
- Backend: `pip install -r requirements.txt`
- Frontend:
 `npm install vite` , `npm install tailwindcss @tailwindcss/vite`, `npm install github-markdown-css`, `npm install marked`


---
### Development 
1. 2 Terminals öffnen (in `/typescript`)
2. *Terminal 1*: start dev-Server: `npm run dev`
3. *Terminal 2*: run program: `cd src`, `python main.py`
---

### Unit-tests (optional)
- install pytest: `pip install pytest`
- write unit-tests in source-files named i.e. `test_yourtest.py` in `/src`
- run tests: `pytest` in `/typescript`
---
