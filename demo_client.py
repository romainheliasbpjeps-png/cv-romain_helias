#!/usr/bin/env python3
"""
Demo Python Client pour PDF to JSON Converter
Exemple d'utilisation de l'API
"""
import sys
import json
from pathlib import Path
import requests


class PDFConverterClient:
    """Client simple pour l'API PDF to JSON"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"

    def health_check(self):
        """Vérifier que l'API est accessible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            sys.exit(1)

    def extract_pdf(
        self,
        pdf_path: Path,
        profile: str = "balanced",
        ocr_mode: str = "auto",
        ocr_lang: str = "fra",
        page_range: str = None
    ):
        """
        Extraire le contenu d'un PDF

        Args:
            pdf_path: Chemin vers le fichier PDF
            profile: fast, balanced, ou accurate
            ocr_mode: auto, on, ou off
            ocr_lang: fra, eng, spa, deu, ita, por
            page_range: Pages à extraire (ex: "1-5")

        Returns:
            dict: Résultat de l'extraction
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {pdf_path}")

        print(f"📄 Extraction de {pdf_path.name}...")
        print(f"   Profil: {profile}")
        print(f"   OCR: {ocr_mode} ({ocr_lang})")

        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            data = {
                'profile': profile,
                'ocr_mode': ocr_mode,
                'ocr_lang': ocr_lang
            }

            if page_range:
                data['page_range'] = page_range

            try:
                response = requests.post(
                    f"{self.api_url}/extract",
                    files=files,
                    data=data,
                    timeout=300  # 5 minutes
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                print("❌ Timeout - Le traitement a pris trop de temps")
                sys.exit(1)
            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur lors de l'extraction: {e}")
                if hasattr(e.response, 'json'):
                    print(e.response.json())
                sys.exit(1)

    def save_result(self, result: dict, output_path: Path):
        """Sauvegarder le résultat dans un fichier JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Résultat sauvegardé: {output_path}")


def main():
    """Fonction principale de démonstration"""
    print("=" * 60)
    print("📄 PDF to JSON Converter - Client Demo")
    print("=" * 60)
    print()

    # Initialiser le client
    client = PDFConverterClient()

    # Health check
    print("🏥 Vérification de l'API...")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   OCR: {health['services']['ocr']}")
    print()

    # Vérifier qu'un fichier PDF est fourni
    if len(sys.argv) < 2:
        print("Usage: python demo_client.py <fichier.pdf> [profile] [ocr_mode]")
        print()
        print("Exemples:")
        print("  python demo_client.py document.pdf")
        print("  python demo_client.py document.pdf accurate on")
        print("  python demo_client.py document.pdf fast off")
        print()
        sys.exit(1)

    # Paramètres
    pdf_path = Path(sys.argv[1])
    profile = sys.argv[2] if len(sys.argv) > 2 else "balanced"
    ocr_mode = sys.argv[3] if len(sys.argv) > 3 else "auto"

    # Extraction
    result = client.extract_pdf(
        pdf_path=pdf_path,
        profile=profile,
        ocr_mode=ocr_mode,
        ocr_lang="fra"
    )

    # Vérifier le succès
    if not result.get('success'):
        print(f"❌ Échec: {result.get('error')}")
        sys.exit(1)

    # Afficher les statistiques
    extraction = result['result']
    doc = extraction['document']
    meta = extraction['meta']

    print()
    print("=" * 60)
    print("✅ Extraction réussie!")
    print("=" * 60)
    print()
    print(f"📊 Statistiques:")
    print(f"   Fichier: {doc['file_name']}")
    print(f"   Taille: {doc['file_size'] / 1024 / 1024:.2f} MB")
    print(f"   Pages: {doc['page_count']}")

    # Compter les éléments
    total_elements = sum(len(page['elements']) for page in extraction['pages'])
    print(f"   Éléments extraits: {total_elements}")

    # Compter par type
    element_types = {}
    for page in extraction['pages']:
        for element in page['elements']:
            elem_type = element['type']
            element_types[elem_type] = element_types.get(elem_type, 0) + 1

    print(f"   Par type:")
    for elem_type, count in sorted(element_types.items()):
        print(f"     - {elem_type}: {count}")

    # Métadonnées
    print()
    print(f"⚙️  Traitement:")
    print(f"   Profil: {extraction['artifacts']['extraction_profile']}")
    print(f"   OCR utilisé: {'Oui' if extraction['artifacts']['ocr_used'] else 'Non'}")
    print(f"   Temps: {meta['processing_time_seconds']:.2f}s")

    # Sauvegarder
    output_path = pdf_path.with_suffix('.json')
    client.save_result(result['result'], output_path)

    print()
    print(f"✨ Terminé! Résultat dans {output_path}")


if __name__ == "__main__":
    main()
