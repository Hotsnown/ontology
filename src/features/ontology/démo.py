from data_preprocessing.data_preprocessing_service import DataPreprocessing
from term_extraction.term_extraction_service import TermExtraction
from term_enrichment.term_enrichment_service import TermEnrichment
from concept_extraction.concept_extraction_service import ConceptExtraction
from concept_hierarchy.concept_hierarchy_service import ConceptHierarchy
from commons.ontology_learning_schema import KR

import pprint

def main() -> None:

    # initialisation
    corpus = ["Le chat se repose sur le lit."]
    candidate_terms = list()
    knowledge_representation = KR()

    # ontology learning process

    # data prep
    data_prep = DataPreprocessing()
    data_prep._set_corpus()

    corpus = data_prep.corpus

    # term extraction --> set global variable candidate_terms

    term_extraction = TermExtraction(data_prep.corpus)
    candidate_terms_by_occurence = term_extraction.on_occurrence_term_extraction()
    candidate_terms_by_pos = term_extraction.on_pos_term_extraction()

    def common_elements(list1, list2):
        return list(set(list1) & set(list2))
    
    candidate_terms = common_elements(candidate_terms_by_occurence, candidate_terms_by_pos)
    
    # term enrichment --> update a list of Candidate Terms

    term_enrich = TermEnrichment(candidate_terms)
    term_enrich.wordnet_term_enrichment()
    enrich_candidate_terms = term_enrich.candidate_terms

    # Concept extraction

    concept_extraction = ConceptExtraction(enrich_candidate_terms)
    concept_extraction.group_by_synonyms()

    kr = concept_extraction.kr

    # Concept hierarchy

    #concept_hierarchy = ConceptHierarchy(corpus, kr)
    #concept_hierarchy.term_subsumption()

    #kr = concept_hierarchy.kr
    pprint.pprint(enrich_candidate_terms)
    print(len(kr.concepts))

if __name__ == "__main__":
    main()
