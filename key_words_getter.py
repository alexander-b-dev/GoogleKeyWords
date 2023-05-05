import traceback
from time import sleep

import google
from google.ads.googleads.client import GoogleAdsClient
from google.api_core.retry import Retry


def getData(queue, googleCustomerID, language, regions, periodFrom, periodTo, inclPartners, inclNSFW, keyWords):
    try:
        client = GoogleAdsClient.load_from_storage(path="google-ads.yaml", version="v12")
        keywordPlanIdeaService = client.get_service("KeywordPlanIdeaService")
        lang = client.get_service("GoogleAdsService").language_constant_path(language)
        queue.put("language")
        geo_target_constants = map_locations_ids_to_resource_names(client, regions)
        queue.put("locations")
        startMonth, startYear = tuple(map(int, periodFrom.split(".")))
        endMonth, endYear = tuple(map(int, periodTo.split(".")))

        for keyWord in keyWords:
            request = client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = googleCustomerID
            request.language = lang
            request.geo_target_constants = geo_target_constants
            request.include_adult_keywords = inclNSFW

            request.historical_metrics_options.year_month_range.start.month = client.get_type("MonthOfYearEnum").MonthOfYear(startMonth)
            request.historical_metrics_options.year_month_range.start.year = startYear
            request.historical_metrics_options.year_month_range.end.month = client.get_type("MonthOfYearEnum").MonthOfYear(endMonth)
            request.historical_metrics_options.year_month_range.end.year = endYear

            if inclPartners:
                request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
            else:
                request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            request.keyword_seed.keywords.append(keyWord)
            keywordIdeas = keywordPlanIdeaService.generate_keyword_ideas(request=request,
                                                                         retry=Retry(predicate=lambda x: isinstance(x, google.api_core.exceptions.ResourceExhausted),
                                                                                     initial=4,
                                                                                     maximum=64,
                                                                                     multiplier=1.5,
                                                                                     deadline=420)
                                                                         )
            res = []
            for idea in keywordIdeas:
                res.append((idea.text, idea.keyword_idea_metrics.avg_monthly_searches))
            queue.put(res)
            sleep(0.5)

        queue.put("done")
    except Exception:
        queue.put(traceback.format_exc())


def map_locations_ids_to_resource_names(client, location_ids):
    build_resource_name = client.get_service("GeoTargetConstantService").geo_target_constant_path
    return [build_resource_name(location_id) for location_id in location_ids]
