from pymongo import MongoClient
from bson import ObjectId


def find_not_affiliated_companies(company_id):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['BusNet']

    # Collections
    affiliation_collection = 'bus network affiliation company'
    enlisted_collection = db['bus network enlisted company']

    try:
        # Convert string ID to ObjectId
        try:
            object_id = ObjectId(company_id)
        except Exception as e:
            print(f"Invalid ObjectId format: {company_id}")
            return []

        # Find the enlisted company by _id
        enlisted_company = enlisted_collection.find_one({"_id": object_id})

        if not enlisted_company:
            print(f"No enlisted company found with _id: {company_id}")
            return []

        print(f"Found enlisted company: {enlisted_company['name']} (_id: {object_id})")

        # Single aggregation query to find non-affiliated companies
        pipeline = [
            # Stage 1: Get all enlisted companies
            {
                "$match": {
                    "_id": {"$ne": object_id}  # Exclude the queried company itself
                }
            },
            # Stage 2: Lookup affiliations to check if company is a target
            {
                "$lookup": {
                    "from": affiliation_collection,
                    "let": {"company_id": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$host_company.id", object_id]},
                                        {"$eq": ["$target_company.id", "$$company_id"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "affiliations"
                }
            },
            # Stage 3: Filter out companies that have affiliations (keep only non-affiliated)
            {
                "$match": {
                    "affiliations": {"$size": 0}
                }
            },
            # Stage 4: Remove the affiliations field from output
            {
                "$project": {
                    "affiliations": 0
                }
            }
        ]

        not_affiliated_companies = enlisted_collection.aggregate(pipeline)

        result = list(not_affiliated_companies)
        print(f"Found {len(result)} companies not affiliated as targets")

        return result

    except Exception as e:
        print(f"Error querying database: {e}")
        return []

    finally:
        client.close()


def main():
    # Example usage
    company_id = input("Enter company _id to find non-affiliated companies: ")

    not_affiliated = find_not_affiliated_companies(company_id)

    if not_affiliated:
        print("\nNon-affiliated companies:")
        print("-" * 50)

        try:
            for company in not_affiliated:
                print(f"ID: {company.get('_id')}")
                print(f"Name: {company.get('name')}")
                print(f"Org Number: {company.get('org_number')}")
                print(f"Country: {company.get('country_code')}")
                print(f"Status: {company.get('status')}")
                print(f"Type: {company.get('type')}")
                print(f"Domain: {company.get('domain')}")
                print("-" * 30)
        except Exception as e:
            print(f"Error printing companies: {e}")
    else:
        print("No non-affiliated companies found.")


if __name__ == "__main__":
    main()
