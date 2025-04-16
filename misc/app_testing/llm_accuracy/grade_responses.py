# Generates a dataset of parsed event responses 
# from the LLM output, which are used to compare the LLM's accuracy
# against expected responses

import os, json, random
import dataclasses
from dataclasses import dataclass
from includes.model import Llama3Model
from includes.email_data import str_to_mail
import traceback, sys

RESPONSES_LOCATION = "./_before_finetune_responses"
GRADED_RESPONSES_LOCATION = "./_graded_before_finetune_responses"
INPUT_OUTPUT_SEPARATOR = "!<-=->!" # for simplicity we use text files which contain stuff separated by this token (input above, output below)
                                   # this will also be the exact same separator for output, which contains generated stuff

@dataclass
class ResponseData:
    file_location: str
    filename: str
    
    mail_data: str
    categories: list[str]
    expected_response: list[dict]
    llm_responses: list[list[dict]]

@dataclass 
class GradeForSingleEvent:
    llm_generated_event: dict
    event_name_grade: float = 0.0
    country_grade: float = 0.0
    city_grade: float = 0.0
    address_grade: float = 0.0
    room_grade: float = 0.0

@dataclass
class GradeForResponse:
    llm_response: list[dict]

    grades_for_each_event: list[GradeForSingleEvent]
    event_finding_grade: float = 0.0

@dataclass
class ManualGradingData:
    expected_response: list[dict]
    exemplars: list[GradeForResponse]

def read_response_file(loc: str) -> ResponseData:
    with open(f"{loc}", "r", encoding="UTF-8") as f:
        content = f.read().split(INPUT_OUTPUT_SEPARATOR)

        return ResponseData(
            file_location=loc,
            filename=os.path.basename(loc),
            
            mail_data=content[0],
            categories=json.loads(content[1]),
            expected_response=json.loads(content[2]),
            llm_responses=[json.loads(resp) for resp in content[3:]]
        )

def read_all_responses(dir: str) -> list[ResponseData]:
    metadatas = []
    for filename in os.listdir(dir):
        obj_loc = f"{dir}/{filename}"

        if(not os.path.isfile(obj_loc)):
            metadatas += read_all_responses(obj_loc)
        elif(filename != "SYS_PROMPT.txt"):
            metadatas.append(
                read_response_file(f"{dir}/{filename}")
            )

    return metadatas

def print_response(custom_text: str, events_response: list[dict]):
    print(f"---------------{custom_text} START-----------------")
    print(json.dumps(events_response, indent="\t"))
    print(f"---------------{custom_text} END-------------------")

def manually_grade(response_data: ResponseData) -> ManualGradingData:
    grading = ManualGradingData(
        expected_response=response_data.expected_response,
        exemplars=[]
    )

    for i, llm_response in enumerate(response_data.llm_responses):
        response_grade = GradeForResponse(
            llm_response,
            grades_for_each_event=[]
        )

        if(len(response_data.expected_response) == 0 and len(llm_response) != 0
           or len(response_data.expected_response) > 0 and len(llm_response) == 0
           ):
            print(f"Skipping exemplar {i+1} for {response_data.filename} because LLM generated events when none are supposed to be there (or vice versa)")
        
        else:            
            for i, event in enumerate(llm_response):
                print_response("EXPECTED RESULT", response_data.expected_response)
                print_response(f"GENERATED EVENT ({i+1}/{len(llm_response)})", response_data.expected_response)

                event_grade = GradeForSingleEvent(event)
                while True:
                    try:
                        event_grade.event_name_grade = float(input("Grade the accuracy of 'event_name' (0.0 -> 1.0): "))
                        event_grade.country_grade = float(input("Grade the accuracy of 'country' (0.0 -> 1.0): "))
                        event_grade.city_grade = float(input("Grade the accuracy of 'city' (0.0 -> 1.0): "))
                        event_grade.address_grade = float(input("Grade the accuracy of 'address' (0.0 -> 1.0): "))
                        event_grade.room_grade = float(input("Grade the accuracy of 'room' (0.0 -> 1.0): "))
                        
                        break
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt
                    except:
                        continue
                response_grade.grades_for_each_event.append(event_grade)

            response_grade.event_finding_grade = float(input("Grade the accuracy of LLM finding correct events (0.0 -> 1.0, correct ÷ total): "))

        grading.exemplars.append(response_grade)
    
    return grading

def add_manual_grading_for_everything(responses: list[ResponseData]):
    for i, response in enumerate(responses):
        grading = manually_grade(response)

        with open(f"{GRADED_RESPONSES_LOCATION}/{response.filename}", "w", encoding="UTF-8") as f:
            f.write(json.dumps(dataclasses.asdict(grading), indent="\t"))
            print(f"Saved grade to file {GRADED_RESPONSES_LOCATION}/{response.filename}")

        print(f"Progress: {i+1}/{len(responses)}")
        print("")
        print("")

generated_responses = read_all_responses(RESPONSES_LOCATION)
add_manual_grading_for_everything(generated_responses)