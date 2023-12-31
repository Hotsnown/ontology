from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import (
    ADJ as WN_ADJ,
    ADV as WN_ADV,
    Lemma,
    NOUN as WN_NOUN,
    Synset,
    VERB as WN_VERB
)
from typing import Any, Dict, List, Optional, Set

from commons.ontology_learning_schema import CandidateTerm
from commons.ontology_learning_utils import underscore2spaceStr, space2underscoreStr
import config.logging_config as logging_config
from term_enrichment.term_enrichment_repository import load_enrichment_wordnet_domains_from_file, load_wordnet_domains

#import wn
#wn = wn.Wordnet('omw-fr:1.4')        # Create Wordnet object to query
#ss = fr.synsets('voiture', pos="n")[0]  # Get the first synset for 'win'
#print(ss.senses())                     # Get the synset's definition

# Adapted from <https://github.com/argilla-io/spacy-wordnet/tree/b9efd800e02d55e848d56ce7acfacafb2089f587>
# The Open Multi Wordnet corpus contains the following languages:
#   als arb bul cat cmn dan ell eus fas fin fra glg heb hrv ind ita jpn nld nno nob pol por qcn slv spa swe tha zsm
#   ('deu' can be found in Extended Open Multi Wordnet)
# the available spacy languages are:
# af am ar bg bn ca cs da de el en es et eu fa fi fr ga gu he hi hr hu hy id is it ja kn ko ky lb lij
# lt lv mk ml mr nb ne nl pl pt ro ru sa si sk sl sq sr sv ta te th ti tl tn tr tt uk ur vi xx yo zh
# then the full mapping is

WORDNET_DOMAINS_SSID_NUM_SIZE = 8

_WN_LANGUAGES_MAPPING = dict(
    es="spa",
    en="eng",
    fr="fra",
    it="ita",
    pt="por",
    de="deu",
    # other languages from omw
    sq="als",  # Albanian
    ar="arb",  # Arabic
    bg="bul",  # Bulgarian
    ca="cat",  # Catalan
    zh="cmn",  # Chinese Open Wordnet
    da="dan",  # Danish
    el="ell",  # Greek
    eu="eus",  # Basque
    fa="fas",  # Persian
    fi="fin",  # Finnish
    # ?? ='glg',  # Galician
    he="heb",  # Hebrew
    hr="hrv",  # Croatian
    id="ind",  # Indonesian
    ja="jpn",  # Japanese
    nl="nld",  # Dutch
    # no ='nno', # Norwegian
    # nb ='nob', # Norwegian Bokmal
    pl="pol",  # Polish
    # ?? ='qcn', # Chinese (Taiwan)
    sl="slv",  # Slovenian
    sv="swe",  # Swedish
    th="tha",  # Thai
    ml="zsm",  # Malayalam
)

_WN_POS_MAPPING = {
    "ADJ": WN_ADJ,
    "NOUN": WN_NOUN,
    "ADV": WN_ADV,
    "VERB": WN_VERB,
    "AUX": WN_VERB,
}


def spacy2wordnet_pos(spacy_pos: str) -> Optional[str]:
    """Tool function to map a Spacy POS tag to the corresponding WordNet one.
        Return None if no mapping is found.
        Adapted from project <https://github.com/argilla-io/spacy-wordnet>


    Parameters
    ----------
    spacy_pos : str
        The Spacy POS tag.

    Returns
    -------
    Optional[str]
        The WordNet POS tag
    """
    return _WN_POS_MAPPING.get(spacy_pos)


def fetch_wordnet_lang(lang: str) -> Optional[str]:
    """Tool function to map a Spacy language tag to the corresponding WordNet one.
        Return None if no mapping is found.
        Adapted from project <https://github.com/argilla-io/spacy-wordnet>

    Parameters
    ----------
    lang : str
        Spacy language tag

    Returns
    -------
    Optional[str]
        The WordNet language tag

    Raises
    ------
    Exception
        An exception to spot a language not existing.
    """
    language = _WN_LANGUAGES_MAPPING.get(lang, None)

    if not language:
        raise Exception(f"Language {lang} not supported")

    return language


class WordNetTermEnrichment:
    """A class to handle WordNet based term enrichment.

    Attributes
    ----------
    options: Dict[str, Any]
        The parameters to setup the class. 
    wordnet_lang: str
        The wordnet language tag to use for enrichment.
    wordnet_domains_map: Dict[str, List[str]] = None
        The mapping of WordNet Synsets to domains, default to None.
    enrichment_domains: Set[str] = None
        The WordNet Synsets domains to consider for term enrichment, default to None.
    wordnet_pos: Set[str] = None
        The WordNet POS tags to consider for term enrichment, default to None.
    """

    def __init__(self, options: Dict[str, Any]) -> None:
        """Initializer for a WordNet based term enrichment process.

        Parameters
        ----------
        options: Dict[str, Any]
            The specific parameters to setup the class.
        """
        self.options = options

        try:
            assert self.options["lang"] is not None
            assert self.options["use_domains"] is not None
            assert self.options["use_pos"] is not None
        except AssertionError as e:
            logging_config.logger.error(
                f"""Config information missing for WordNet term enrichment. Make sure you provided the configuration fields:
                    - term_enrichment.wordnet.lang
                    - term_enrichment.wordnet.use_domain
                    - term_enrichment.wordnet.use_pos
                    Trace : {e}
                """)

        self.wordnet_lang = fetch_wordnet_lang(self.options["lang"])
        self.wordnet_domains_map: Dict[str, List[str]] = None
        self.enrichment_domains: Set[str] = None
        self.wordnet_pos: Set[str] = None

        if self.options["use_domains"]:
            self.wordnet_domains_map = load_wordnet_domains()
            self._get_enrichment_domains()

        if self.options["use_pos"]:
            self._get_wordnet_pos()


    def _get_enrichment_domains(self) -> None:
        """Private method to get a list of WordNet domains to use for term enrichment.
            The domains are fetched based on the configuration details.

            This method affects the attribute self.enrichment_domains
        """
        try:
            domains = self.options["enrichment_domains"]
        except KeyError as e:
            logging_config.logger.error(
                f"""Using enrichment wordnet domains (use_domains = True) but config parameter `enrichment_domains` is not provided.
                    Trace : {e}
                """)

        if domains is not None:
            if len(domains) > 0:
                self.enrichment_domains = set(domains)
            else:
                logging_config.logger.warn(
                    f"""Using enrichment wordnet domains but config parameter `enrichment_domains` is an empty list.  
                    """)
        else:
            self.enrichment_domains = load_enrichment_wordnet_domains_from_file()

        if not self._check_domains_exist():
            logging_config.logger.warn(
                f"""Some Wordnet domains have not been found in the mappings.  
                """)

    def _check_domains_exist(self) -> bool:
        """Private method to test wether all the WordNet domains provided for enrichment 
            exist in the mapping of WordNet Synsets to domains

        Returns
        -------
        bool
            Wether or not all the WordNet domains provided for enrichment exist.
        """
        all_wordnet_domains = set()
        for synset_domains in self.wordnet_domains_map.values():
            all_wordnet_domains.update(set(synset_domains))

        domains_exist = self.enrichment_domains.issubset(all_wordnet_domains)

        return domains_exist

    def _get_wordnet_pos(self) -> None:
        """Private method to get a list of WordNet POS tags to use for term enrichment.
            The POS tags are fetched based on the configuration details.

            This method affects the attribute self.wordnet_pos
        """
        try:
            config_pos = self.options["synset_pos"]
        except KeyError as e:
            logging_config.logger.error(
                f"""Using POS tags (use_pos = True) but config parameter `synset_pos` is not provided.
                    Trace : {e}
                """)

        if isinstance(config_pos, list):
            self.wordnet_pos = {spacy2wordnet_pos(pos) for pos in config_pos}
        else:
            logging_config.logger.warn(
                f"""Using specified POS but config parameter `synset_pos` is an empty.  
                    """)

    def _get_domains_for_synset(self, synset: Synset) -> Set[str]:
        """Private method to extract the domains associated with a WordNet Sysnset.
            Adapted from project <https://github.com/argilla-io/spacy-wordnet>

        Parameters
        ----------
        synset : Synset
            The WordNet Synset to extract the domains from.

        Returns
        -------
        Set[str]
            The set of domains associated with the synset
        """
        ssid = "{}-{}".format(str(synset.offset()
                                  ).zfill(WORDNET_DOMAINS_SSID_NUM_SIZE), synset.pos())
        synset_domains = self.wordnet_domains_map.get(ssid, set())

        return synset_domains

    def _find_wordnet_domains(self, synsets: Set[Synset]) -> Set[str]:
        """A private tool method to fecth the WordNet domains associated with a set of Synsets. 

        Parameters
        ----------
        synsets : Set[Synset]
            The set of WordNet Synsets to extract the domains from. 

        Returns
        -------
        Set[str]
            The set of WordNet domains
        """

        wordnet_domains = {
            domain
            for synset in synsets
            for domain in self._get_domains_for_synset(synset)
        }

        return wordnet_domains

    def _filter_synsets_on_domains(self, synsets: Set[Synset]) -> Set[Synset]:
        """Private method to filter out synsets not associated with the WordNet domains
            to use for term enrichment.

        Parameters
        ----------
        synsets : Set[Synset]
            The set of WordNet synsets to filter.

        Returns
        -------
        Set[Synset]
            The filtered set of synsets.
        """
        kept_synsets = set()

        for synset in synsets:
            synset_domains = self._get_domains_for_synset(synset)
            if len(self.enrichment_domains.intersection(synset_domains)):
                kept_synsets.add(synset)

        return kept_synsets

    def enrich_candidate_term(self, candidate_term: CandidateTerm) -> None:
        """The method to enrich one candidate term.

        Parameters
        ----------
        candidate_term : CandidateTerm
            The candidate term to enrich.
        """
        term_wordnet_text = space2underscoreStr(candidate_term.value)

        term_synsets = self._get_term_wordnet_synsets(term_wordnet_text)

        candidate_term.synonyms.update(self._get_term_synonyms(term_synsets))

        candidate_term.hypernyms.update(self._get_term_hypernyms(term_synsets))

        candidate_term.hyponyms.update(self._get_term_hyponyms(term_synsets))

        candidate_term.antonyms.update(self._get_term_antonyms(term_synsets))

    def enrich_candidate_terms(self, candidate_terms: List[CandidateTerm]) -> None:
        """The main method of the class. It enriches a list of candidate terms.

        Parameters
        ----------
        candidate_terms : List[CandidateTerm]
            The list of candidate terms to enrich.
        """
        for term in candidate_terms:
            self.enrich_candidate_term(term)

    def _get_lemmas_texts(self, lemmas: Set[Lemma]) -> Set[str]:
        """Private method to extract the strings associated with a set of WordNet Lemmas.

        Parameters
        ----------
        lemmas : Set[Lemma]
            The set of Lemmas to extract the strings from.

        Returns
        -------
        Set[str]
            The set of extracted strings.
        """
        lemmas_names = set()

        for lemma in lemmas:
            lemmas_names.add(lemma.name())

            for derived_lemma in lemma.derivationally_related_forms():
                lemmas_names.add(derived_lemma.name())

        lemmas_texts = {underscore2spaceStr(name) for name in lemmas_names}

        return lemmas_texts

    def _get_term_synonyms(self, term_synsets: Set[Synset]) -> Set[str]:
        """Private method to extract the synonyms (strings) from a set of WordNet Synsets.

        Parameters
        ----------
        term_synsets : Set[Synset]
            The set of WordNet Synsets to extract the synonyms from.

        Returns
        -------
        Set[str]
            The set of synonyms strings.
        """
        term_synonyms = set()
        for synset in term_synsets:  # the term synonyms are the Synsets
            synset_lemmas = synset.lemmas(lang=self.wordnet_lang)
            synset_lemmas_texts = self._get_lemmas_texts(synset_lemmas)
            term_synonyms.update(synset_lemmas_texts)

        return term_synonyms

    def _get_term_hypernyms(self, term_synsets: Set[Synset]) -> Set[str]:
        """Private method to extract the hypernyms (strings) from a set of WordNet Synsets.

        Parameters
        ----------
        term_synsets : Set[Synset]
            The set of WordNet Synsets to extract the hypernyms from.

        Returns
        -------
        Set[str]
            The set of hypernyms strings.
        """

        # extract hypernyms Synsets
        term_hypernyms_synsets = set()
        for synset in term_synsets:
            synset_hypernyms = self._get_synset_hypernyms(synset)
            term_hypernyms_synsets.update(synset_hypernyms)

        # extract lemmas texts from hypernyms Synsets
        term_hypernyms = set()
        for synset in term_hypernyms_synsets:
            synset_lemmas = synset.lemmas(lang=self.wordnet_lang)
            synset_lemmas_texts = self._get_lemmas_texts(synset_lemmas)
            term_hypernyms.update(synset_lemmas_texts)

        return term_hypernyms

    def _get_term_hyponyms(self, term_synsets: Set[Synset]) -> Set[str]:
        """Private method to extract the hyponyms (strings) from a set of WordNet Synsets.

        Parameters
        ----------
        term_synsets : Set[Synset]
            The set of WordNet Synsets to extract the hyponyms from.

        Returns
        -------
        Set[str]
            The set of hyponyms strings.
        """

        # extract hyponyms Synsets
        term_hyponyms_synsets = set()
        for synset in term_synsets:
            synset_hyponyms = self._get_synset_hyponyms(synset)
            term_hyponyms_synsets.update(synset_hyponyms)

        # extract lemmas texts from hyponyms Synsets
        term_hyponyms = set()
        for synset in term_hyponyms_synsets:
            synset_lemmas = synset.lemmas(lang=self.wordnet_lang)
            synset_lemmas_texts = self._get_lemmas_texts(synset_lemmas)
            term_hyponyms.update(synset_lemmas_texts)

        return term_hyponyms

    def _get_term_antonyms(self, term_synsets: Set[Synset]) -> Set[str]:
        """Private method to extract the antonyms (strings) from a set of WordNet Synsets.

        Parameters
        ----------
        term_synsets : Set[Synset]
            The set of WordNet Synsets to extract the antonyms from.

        Returns
        -------
        Set[str]
            The set of antonyms strings.
        """
        term_antonyms_lemmas = set()
        for synset in term_synsets:
            # antonyms are linked with Lemmas in WordNet
            # extract synsets lemmas
            synset_lemmas = synset.lemmas(lang=self.wordnet_lang)
            synset_antonyms = set()

            # Extract lemmas antonyms
            for lemma in synset_lemmas:
                synset_antonyms.update(set(lemma.antonyms()))

            term_antonyms_lemmas.update(synset_antonyms)

        term_antonyms_texts = self._get_lemmas_texts(term_antonyms_lemmas)

        return term_antonyms_texts

    def _get_term_wordnet_synsets(self, term_text: str) -> Set[Synset]:
        """Private method to get WordNet Synsets associated with a term string.

        Parameters
        ----------
        term_text : str
            The term string

        Returns
        -------
        Set[Synset]
            The corresponding WordNet Synsets
        """
        term_synsets = set()

        if self.options["use_pos"]:
            for pos in self.wordnet_pos:
                term_synsets.update(
                    set(wn.synsets(term_text, pos=pos, lang=self.wordnet_lang)))
        else:
            term_synsets.update(
                set(wn.synsets(term_text, lang=self.wordnet_lang)))

        if self.options["use_domains"]:
            term_synsets = self._filter_synsets_on_domains(
                synsets=term_synsets)

        return term_synsets

    def _get_synset_hypernyms(self, synset: Synset) -> Set[Synset]:
        """Private method to get WordNet hypernyms Synsets associated with a Synset.

        Parameters
        ----------
        synset : Synset
            The Synset to extract the hypernyms from.

        Returns
        -------
        Set[Synset]
            The hypernyms Synsets
        """
        synset_hypernyms = set(synset.hypernyms())

        if self.options["use_domains"]:
            synset_hypernyms = self._filter_synsets_on_domains(
                synsets=synset_hypernyms)

        return synset_hypernyms

    def _get_synset_hyponyms(self, synset: Synset) -> Set[Synset]:
        """Private method to get WordNet hyponyms Synsets associated with a Synset.

        Parameters
        ----------
        synset : Synset
            The Synset to extract the hyponyms from.

        Returns
        -------
        Set[Synset]
            The hyponyms Synsets
        """
        synset_hyponyms = set(synset.hyponyms())

        if self.options["use_domains"]:
            synset_hyponyms = self._filter_synsets_on_domains(
                synsets=synset_hyponyms)

        return synset_hyponyms
