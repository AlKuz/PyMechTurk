"""
The MTurk XML QuestionForm page for qualification test:
https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QuestionFormDataStructureArticle.html

The MTurk XML AnswerKey page for qualification test:
https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_AnswerKeyDataStructureArticle.html

The main descriptions of the classes was copied from the link above
"""

from typing import Optional, List, Dict
from xml.dom import minidom
import xml.etree.ElementTree as ET
import re


class XMLWrapper(object):
    """Base class for compiling XML QuestionForm"""

    def __init__(self):
        self._elements: List[ET.Element] = list()
        self._attributes = dict()

    def __len__(self):
        """Get number of elements"""
        return len(self._elements)

    def to_string(self, root_name: Optional[str] = None,
                  url_safe: bool = False,
                  formatted: bool = True,
                  indent: int = 4) -> str:
        tree = self.compile_elements(root_name)
        tree_str = ET.tostring(tree, encoding="ascii", method="xml").decode("ascii")
        if formatted:
            tree_str = minidom.parseString(tree_str).toprettyxml(indent=' ' * indent)
        tree_str = re.sub(r"<\?xml.*\?>", '', tree_str)[1:]
        if url_safe:
            tree_str = self._encode_for_url(tree_str)
        return tree_str

    def save(self, path: str,
             root_name: Optional[str] = None,
             url_safe: bool = False,
             formatted: bool = True,
             indent: int = 4):
        tree_str = self.to_string(root_name, url_safe=url_safe, formatted=formatted, indent=indent)
        with open(path, "w") as file:
            file.write(tree_str)

    @staticmethod
    def _encode_for_url(text: str) -> str:
        """
        Data must be URL encoded to appear as a single parameter value in the request. Characters that are part of URL
        syntax, such as question marks (?) and ampersands (&), must be replaced with the corresponding URL character
        codes.
        """
        encoder = [
            ("$", "%24"),
            ("&", "%26"),
            ("+", "%2B"),
            (",", "%2C"),
            ("/", "%2F"),
            (":", "%3A"),
            (";", "%3B"),
            ("?", "%3F"),
            ("@", "%40")
        ]
        for char, code in encoder:
            text = text.replace(char, code)
        return text

    def compile_elements(self, root_name: Optional[str] = None) -> ET.Element:
        """
        Generate XML tree with given name.

        Args:
            root_name (Optional[str]): The name of the XML tree root. If None it use the class name

        Returns:
            xml.Element: Generated XML tree with given name
        """
        if not root_name:
            root_name = self.__class__.__name__
        root = ET.Element(root_name, attrib=self._attributes)
        for element in self._elements:
            root.append(element)
        return root


class Content(XMLWrapper):
    """
    The Overview elements and the QuestionContent elements of a QuestionForm can contain different types of
    information. For example, you might include a paragraph of text and an image in your HIT's overview.
    """

    def add_title(self, title: str) -> "Content":
        """
        A Title element specifies a string to be rendered as a title or heading.

        Args:
            title (str): Title text

        Returns:
            Content: The Content object with additional title field
        """
        element = ET.Element("Title")
        element.text = title
        self._elements.append(element)
        return self

    def add_text(self, text: str) -> "Content":
        """
        A Text element specifies a block of text to be rendered as a paragraph. Only plain text is allowed. HTML is not
        allowed. If HTML characters (such as angle brackets) are included in the data, they appear verbatim in the web
        output.

        Args:
            text (str): The text to add in paragraph

        Returns:
            Content: The Content object with additional text field
        """
        element = ET.Element("Text")
        element.text = text
        self._elements.append(element)
        return self

    def add_formatted_text(self, text: str) -> "Content":
        """
        Formatted content is a block of text with formatting information specified using XHTML tags. For example, you
        can use XHTML tags to specify that certain words appear in a boldface font or to include a table in your HIT
        information.

        For getting information about allowed tags read the link:
        https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_FormattedContentXHTMLArticle.html

        Args:
            text (str): XHTML formatted text

        Returns:
            Content: The Content object with additional formatted content field
        """
        element = ET.Element("FormattedContent")
        element.text = f"<![CDATA[{text}]]>"
        self._elements.append(element)
        return self

    def add_list(self, items: List[str]) -> "Content":
        """
        A List element displays a bulleted list of items. Items are specified using one or more ListItem elements
        inside the List. The ListItem element is a string.

        Args:
            items (List[str]): List of items

        Returns:
            Content: The Content object with additional list of elements field
        """
        list_of_elements = ET.Element("List")
        for i in items:
            item = ET.SubElement(list_of_elements, "ListItem")
            item.text = i
        self._elements.append(list_of_elements)
        return self

    def add_image(self, url: str, alt_text: str = "image") -> "Content":
        """
        Add image to the content

        Args:
            url (str): URL path to the image
            alt_text (str): The text that should appear if the data cannot be rendered in the browser.

        Returns:
            Content: The Content object with additional image field
        """
        element = ET.Element("Binary")

        mime_type_elem = ET.SubElement(element, "MimeType")
        name = ET.SubElement(mime_type_elem, "Type")
        name.text = "image"
        if url.split(".")[-1]:
            name = ET.SubElement(mime_type_elem, "SubType")
            name.text = url.split(".")[-1]

        data_url_elem = ET.SubElement(element, "DataURL")
        data_url_elem.text = url

        alt_text_elem = ET.SubElement(element, "AltText")
        alt_text_elem.text = alt_text

        self._elements.append(element)
        return self


class Answer(XMLWrapper):
    """Empty class, only for creating class tree"""


class FreeTextAnswer(Answer):
    """
    A FreeTextAnswer element describes a text field and constraints on its possible values.
    """

    def __init__(self, default_text: Optional[str] = None,
                 lines_in_box: Optional[int] = None,
                 reg_exp: Optional[str] = None,
                 error_text: Optional[str] = None,
                 min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 is_numeric: bool = False,
                 min_val: Optional[int] = None,
                 max_val: Optional[int] = None):
        """
        Create new answer field.

        Args:
            default_text (str): Specifies default text. This value appears in the form when
                it is rendered, and is accepted as the answer if the Worker does
                not change it.
            lines_in_box (int): Specifies how tall the form field should be, if
                possible. The field might be rendered as a text box with this many
                lines, depending on the device the Worker is using to see the form.
            reg_exp (Optional[str]): Specifies that JavaScript validates the answer
                string against a given pattern.
            error_text (Optional[str]): Message if regular expression was failed.
            min_length (Optional[int]): Minimum number of characters.
            max_length (Optional[int]): Maximum number of characters.
            is_numeric (bool): Specifies that the value entered must be numeric. If True the reg_exp, error_text,
                min_length, max_length are not used.
            min_val (Optional[int]): Minimum value of the number. Needs 'is_numeric' flag.
            max_val (Optional[int]): Maximum value of the number. Needs 'is_numeric' flag.
        """
        super().__init__()
        if any([reg_exp, min_length, max_length, is_numeric]):
            self._add_constraints(reg_exp, error_text, min_length, max_length, is_numeric, min_val, max_val)
        if default_text:
            self._add_text(default_text)
        if lines_in_box:
            self._set_number_of_lines(lines_in_box)

    def _add_constraints(self, reg_exp: Optional[str] = None,
                         error_text: Optional[str] = None,
                         min_length: Optional[int] = None,
                         max_length: Optional[int] = None,
                         is_numeric: bool = False,
                         min_val: Optional[int] = None,
                         max_val: Optional[int] = None):

        constraints = ET.Element("Constraints")
        if reg_exp and not is_numeric:
            element = self._create_reg_exp(reg_exp, error_text)
            constraints.append(element)
        if any([min_length, max_length]) and not is_numeric:
            element = self._add_length_constraints(min_length, max_length)
            constraints.append(element)
        if is_numeric:
            element = self._create_is_numeric(min_val, max_val)
            constraints.append(element)
        self._elements.append(constraints)

    @staticmethod
    def _create_reg_exp(reg_exp: str, error_text: Optional[str]) -> ET.Element:
        attrib = dict()
        attrib["regex"] = reg_exp
        if error_text:
            attrib["errorText"] = error_text
        return ET.Element("AnswerFormatRegex", attrib=attrib)

    @staticmethod
    def _add_length_constraints(min_length: Optional[int], max_length: Optional[int]) -> ET.Element:
        attrib = dict()
        if min_length:
            attrib["minLength"] = str(min_length)
        if max_length:
            attrib["maxLength"] = str(max_length)
        return ET.Element("Length", attrib=attrib)

    @staticmethod
    def _create_is_numeric(min_val: Optional[int], max_val: Optional[int]) -> ET.Element:
        attrib = dict()
        if min_val:
            attrib["minValue"] = str(min_val)
        if max_val:
            attrib["maxValue"] = str(max_val)
        return ET.Element("IsNumeric", attrib=attrib)

    def _set_number_of_lines(self, num_lines: int):
        element = ET.Element("NumberOfLinesSuggestion")
        element.text = str(num_lines)
        self._elements.append(element)

    def _add_text(self, text: str):
        element = ET.Element("DefaultText")
        element.text = text
        self._elements.append(element)


class SelectionAnswer(Answer):
    """
    A SelectionAnswer describes a multiple-choice question. Depending on the
    element defined, the Worker might be able to select zero, one, or multiple
    items from a set list as the answer to the question.
    """

    def __init__(self, selections: Dict[str, str],
                 answer_style: Optional[str] = None,
                 min_selections: Optional[int] = None,
                 max_selections: Optional[int] = None):
        """
        Create new answer field.

        Args:
            selections (dict): The dictionary of {answer_id: answer_text}
            answer_style (Optional[str]): Specifies what style of multiple-choice form field to use when displaying
                the question to the Worker. The field might not use the suggested style, depending on the device the
                Worker is using to see the form. Allowed values:
                    - radiobutton
                    - dropdown
                    - ...
            min_selections (Optional[int]): Specifies the minimum number of selections allowed for a valid answer.
                This value can range from 0 to the number of selections. Default 1.
            max_selections (Optional[int]): Specifies the maximum number of selections allowed for a valid answer.
                This value can range from 1 to the number of selections. Default 1.
        """
        super().__init__()
        if min_selections:
            self._add_min_selections(min_selections)
        if max_selections:
            self._add_max_selections(max_selections)
        if answer_style:
            self._add_answer_style(answer_style)
        self._add_selections(selections)

    def _add_min_selections(self, number: int):
        element = ET.Element("MinSelectionCount")
        element.text = number
        self._elements.append(element)

    def _add_max_selections(self, number: int):
        element = ET.Element("MaxSelectionCount")
        element.text = number
        self._elements.append(element)

    def _add_answer_style(self, style: str):
        element = ET.Element("StyleSuggestion")
        element.text = style
        self._elements.append(element)

    def _add_selections(self, selections: Dict[str, str]):
        element = ET.Element("Selections")
        for i, s in selections.items():
            item = ET.SubElement(element, "Selection")
            sel_id = ET.SubElement(item, "SelectionIdentifier")
            sel_id.text = i
            text = ET.SubElement(item, "Text")
            text.text = s
        self._elements.append(element)


class Question(XMLWrapper):
    _ID = 1

    def __init__(self, content: Content,
                 answer: Answer,
                 name: Optional[str] = None,
                 is_required: bool = False,
                 question_id: Optional[str] = None):
        super().__init__()
        self._question_id = question_id if question_id else f"QuestionID_{self._ID}"
        self._add_id()
        if name:
            self._add_name(name)
        self._add_is_required(is_required)
        self._add_content(content)
        self._add_answer(answer)

    @property
    def id(self) -> str:
        return self._question_id

    def _add_id(self):
        element = ET.Element("QuestionIdentifier")
        element.text = self._question_id
        self.__class__._ID += 1
        self._elements.append(element)

    def _add_name(self, name: str):
        element = ET.Element("DisplayName")
        element.text = name
        self._elements.append(element)

    def _add_is_required(self, is_required: bool):
        element = ET.Element("IsRequired")
        element.text = "true" if is_required else "false"
        self._elements.append(element)

    def _add_content(self, content: Content):
        self._elements.append(content.compile_elements("QuestionContent"))

    def _add_answer(self, answer: Answer):
        element = ET.Element("AnswerSpecification")
        element.append(answer.compile_elements())
        self._elements.append(element)


class QuestionForm(XMLWrapper):
    """
    The top-most element of the QuestionForm data structure is a QuestionForm element. This element contains optional
    Overview elements and one or more Question elements. There can be any number of these two element types listed
    in any order.
    """

    def __init__(self):
        super().__init__()
        self._attributes["xmlns"] = \
            "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2017-11-06/QuestionForm.xsd"

    def add_overview(self, overview: Content) -> "QuestionForm":
        """
        The Overview element describes instructions and information, and presents them separately from the set of
        questions. It can contain any kind of informational content, as described below. If omitted, no overview text
        is displayed above the questions.

        Args:
            overview (Content): The overview element.

        Returns:
            QuestionForm: Return self with updated field.
        """
        self._elements.append(overview.compile_elements("Overview"))
        return self

    def add_question(self, question: Question) -> "QuestionForm":
        """
        The Question structure.

        Args:
            question (Question): The question element.

        Returns:
            QuestionForm: Return self with updated field.
        """
        self._elements.append(question.compile_elements("Question"))
        return self


class AnswerKey(XMLWrapper):
    def __init__(self):
        super().__init__()
        self._attributes["xmlns"] = \
            "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/AnswerKey.xsd"
        self._is_score_added = False

    def add_max_score(self, score: int) -> "AnswerKey":
        assert not self._is_score_added, "Score was already added to the answers"

        element = ET.Element("QualificationValueMapping")
        percentage = ET.SubElement(element, "PercentageMapping")
        max_score = ET.SubElement(percentage, "MaximumSummedScore")
        max_score.text = str(score)

        self._elements.append(element)
        self._is_score_added = True
        return self

    def add_question_keys(self, question: Question, keys: Dict[int, List[str]]) -> "AnswerKey":
        """
        Keys for the Question

        Args:
            question (Question): The Question object for whom the answers are prepared
            keys (Dict[int, List[str]]): The keys dictionary {answer_score: [the_options_which_fit_for_the_score]}
        """
        element = ET.Element("Question")
        element.append(self._create_question_id(question.id))
        element.extend(self._create_question_keys(keys))
        self._elements.append(element)
        return self

    @staticmethod
    def _create_question_id(question_id: str) -> ET.Element:
        element = ET.Element("QuestionIdentifier")
        element.text = question_id
        return element

    @staticmethod
    def _create_question_keys(keys: Dict[int, List[str]]) -> List[ET.Element]:
        elements = list()
        for score, answers in keys.items():
            option = ET.Element("AnswerOption")

            for a in answers:
                answer_element = ET.SubElement(option, "SelectionIdentifier")
                answer_element.text = a

            score_element = ET.SubElement(option, "AnswerScore")
            score_element.text = str(score)

            elements.append(option)
        return elements
