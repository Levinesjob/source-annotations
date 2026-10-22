"""Build a whitelist-only local preview archive; never uploads or publishes."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
folders = ('agents','assets','docs','examples','output','references','scripts','tests','.github')
names = ('SKILL.md','README.md','PROJECT.md','LICENSE','THIRD_PARTY_NOTICES.md','requirements.txt',
         'requirements-showcase.txt','CHANGELOG.md','TODO.md','.gitignore','.gitattributes')
files = [root/n for n in names]
files += [p for folder in folders for p in (root/folder).rglob('*')
          if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
files += [root/'review/STATUS.md',root/'review/REQUEST.md',root/'review/ACADEMIC-REGRESSION.md',root/'review/ATTENTION-2026-10-18.md',root/'review/ATTENTION-STATIC-2026-10-18.md',root/'review/RELEASE-2026-10-22.md']
destination = root/'local/dist/source-annotations-current.zip'
destination.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(files):
        archive.write(file, 'source-annotations/'+file.relative_to(root).as_posix())
print(destination)
print(f'{len(files)} whitelist files; local/, .venv/, private review transcripts excluded')
