from pymongo import MongoClient


def find_not_affiliated_companies(org_number):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['BusNet']

    # Collections
    affiliation_collection = db['bus network affiliation company']
    enlisted_collection = db['bus network enlisted company']

    try:
        # Find the enlisted company by org_number
        enlisted_company = enlisted_collection.find_one({"org_number": org_number})

        if not enlisted_company:
            print(f"No enlisted company found with org_number: {org_number}")
            return []

        print(f"Found enlisted company: {enlisted_company['name']}")

        # Get all affiliations where this company is either host or target
        affiliated_org_numbers = set()

        # Find affiliations where this company is the host
        host_affiliations = affiliation_collection.find({
            "host_company.org_number": org_number,
            "status": "accepted"
        })

        for affiliation in host_affiliations:
            affiliated_org_numbers.add(affiliation['target_company']['org_number'])

        # Find affiliations where this company is the target
        target_affiliations = affiliation_collection.find({
            "target_company.org_number": org_number,
            "status": "accepted"
        })

        for affiliation in target_affiliations:
            affiliated_org_numbers.add(affiliation['host_company']['org_number'])

        # Find all enlisted companies that are NOT affiliated
        # Create a list of org_numbers to exclude (affiliated companies + the queried company)
        excluded_org_numbers = list(affiliated_org_numbers)
        excluded_org_numbers.append(org_number)

        not_affiliated_companies = enlisted_collection.find({
            "org_number": {"$nin": excluded_org_numbers}
        })

        result = list(not_affiliated_companies)
        print(f"Found {len(result)} non-affiliated companies")

        return result

    except Exception as e:
        print(f"Error querying database: {e}")
        return []

    finally:
        client.close()


def main():
    # Example usage
    org_number = input("Enter org_number to find non-affiliated companies: ")

    not_affiliated = find_not_affiliated_companies(org_number)

    if not_affiliated:
        print("\nNon-affiliated companies:")
        print("-" * 50)

        try:
            for company in not_affiliated:
                print(f"Name: {company.get('name')}")
                print(f"Org Number: {company.get('org_number')}")
                print(f"Country: {company.get('country_code')}")
                print(f"Status: {company.get('status')}")
                print("-" * 30)
        except Exception as e:
            print(f"Error printing companies: {e}")
    else:
        print("No non-affiliated companies found.")


if __name__ == "__main__":
    main()